# src/rag_pipeline.py
# ─────────────────────────────────────────────
# RAG Pipeline: Document ingestion → Chunking →
# Embedding → ChromaDB storage → Retrieval
# ─────────────────────────────────────────────

import os
import glob
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from google import genai
import chromadb

from src.config import (
    GEMINI_API_KEY, EMBEDDING_MODEL, CHROMA_DB_DIR,
    COLLECTION_NAME, CHUNK_SIZE, CHUNK_OVERLAP, TOP_K_RESULTS, DATA_DIR
)


class LocalRAGPipeline:
    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.chroma_client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
        self.collection = self.chroma_client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )

    # ── Embedding ─────────────────────────────────────────────────────────────

    def get_embedding(self, text: str) -> list[float]:
        """Generates a 768-dim embedding vector using Gemini text-embedding-004."""
        response = self.client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=text
        )
        return response.embeddings[0].values

    # ── Ingestion ─────────────────────────────────────────────────────────────

    def ingest_document(self, doc_name: str, content: str):
        """Chunks a document and stores embeddings in ChromaDB."""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", " ", ""]
        )
        chunks = splitter.split_text(content)

        for idx, chunk in enumerate(chunks):
            chunk_id = f"{doc_name}_chunk_{idx}"

            # Skip if already indexed (prevents re-ingestion on restart)
            existing = self.collection.get(ids=[chunk_id])
            if existing["ids"]:
                continue

            embedding = self.get_embedding(chunk)
            self.collection.add(
                ids=[chunk_id],
                embeddings=[embedding],
                metadatas=[{
                    "source": doc_name,
                    "chunk_index": idx,
                    "total_chunks": len(chunks)
                }],
                documents=[chunk]
            )

        return len(chunks)

    def ingest_all_documents(self) -> dict:
        """
        Scans the /data directory and ingests all supported file types:
        .txt, .md, .pdf
        Returns a summary of what was ingested.
        """
        summary = {}
        patterns = ["*.txt", "*.md", "*.pdf"]

        for pattern in patterns:
            files = glob.glob(os.path.join(DATA_DIR, pattern))
            for filepath in files:
                doc_name = os.path.basename(filepath)
                content = self._parse_file(filepath)
                if content:
                    n_chunks = self.ingest_document(doc_name, content)
                    summary[doc_name] = n_chunks

        return summary

    def _parse_file(self, filepath: str) -> str:
        """Reads and returns raw text from .txt, .md, or .pdf files."""
        ext = os.path.splitext(filepath)[1].lower()

        if ext in [".txt", ".md"]:
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()

        elif ext == ".pdf":
            reader = PdfReader(filepath)
            text = ""
            for page_num, page in enumerate(reader.pages):
                extracted = page.extract_text()
                if extracted:
                    text += f"\n[Page {page_num + 1}]\n{extracted}\n"
            return text

        return ""

    # ── Retrieval ─────────────────────────────────────────────────────────────

    def retrieve_context(self, query: str, top_k: int = TOP_K_RESULTS) -> list[dict]:
        """
        Embeds the query and retrieves the top-k most similar chunks
        from ChromaDB using cosine similarity.

        Returns list of dicts: { text, source, score, chunk_index }
        """
        if self.collection.count() == 0:
            return []

        query_vector = self.get_embedding(query)

        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=min(top_k, self.collection.count())
        )

        retrieved_items = []
        if results and results["documents"]:
            for i in range(len(results["documents"][0])):
                # ChromaDB with cosine space returns distances (0=identical, 2=opposite)
                # Convert to similarity score: 1 - (distance / 2) → range [0, 1]
                raw_distance = results["distances"][0][i] if results.get("distances") else 0.0
                similarity_score = round(1.0 - (raw_distance / 2.0), 4)

                retrieved_items.append({
                    "text": results["documents"][0][i],
                    "source": results["metadatas"][0][i]["source"],
                    "chunk_index": results["metadatas"][0][i].get("chunk_index", 0),
                    "score": similarity_score
                })

        # Sort by score descending
        retrieved_items.sort(key=lambda x: x["score"], reverse=True)
        return retrieved_items

    def get_collection_stats(self) -> dict:
        """Returns stats about the current vector DB collection."""
        return {
            "total_chunks": self.collection.count(),
            "collection_name": COLLECTION_NAME,
            "db_dir": CHROMA_DB_DIR
        }
