# 🤖 Persona-Adaptive Customer Support Agent

An intelligent customer support agent that automatically detects customer personas, retrieves relevant knowledge base articles using RAG, generates persona-appropriate responses, and escalates to human agents when necessary.

---

## 📋 Project Overview

This system classifies customers into one of three personas — **Technical Expert**, **Frustrated User**, or **Business Executive** — and adapts its response tone and style accordingly. It uses a RAG pipeline backed by ChromaDB and Google Gemini embeddings to ensure all responses are grounded in factual support documentation with no hallucination.

---

## 🛠️ Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Language | Python | 3.11+ |
| LLM | Google Gemini 2.5 Flash | Latest |
| Embeddings | Gemini text-embedding-004 | Latest |
| Vector DB | ChromaDB | >=0.4.0 |
| RAG Framework | LangChain | >=0.1.0 |
| UI | Streamlit | >=1.30.0 |
| PDF Parsing | pypdf | >=3.0.0 |
| Env Management | python-dotenv | >=1.0.0 |

---

## 🏗️ Architecture Diagram

```
User Query
    │
    ▼
┌─────────────────────┐
│  Persona Classifier  │  (Gemini 2.5 Flash + Structured JSON Output)
│  classifier.py       │  → Technical Expert / Frustrated User / Business Executive
└─────────┬───────────┘
          │  Persona Tag + Confidence
          ▼
┌─────────────────────┐
│   RAG Pipeline       │  (LangChain Chunker + Gemini Embeddings + ChromaDB)
│   rag_pipeline.py    │  → Top-3 relevant document chunks (cosine similarity)
└─────────┬───────────┘
          │  Context Chunks + Similarity Scores
          ▼
┌─────────────────────┐
│  Escalation Check    │  (escalator.py)
│                      │  • Confidence < 0.45 → Escalate
│                      │  • Sensitive keyword detected → Escalate
│                      │  • 3+ consecutive frustrated turns → Escalate
└────┬──────────┬──────┘
     │          │
     │ No       │ Yes
     ▼          ▼
┌──────────┐  ┌────────────────────┐
│ Adaptive │  │ Escalate to Human  │
│ Response │  │ + Generate Handoff │
│ Generator│  │   JSON Summary     │
│generator │  │   escalator.py     │
│  .py     │  └────────────────────┘
└──────────┘
     │
     ▼
┌─────────────────────┐
│  Streamlit UI        │  app.py
│  • Persona badge     │
│  • Retrieved sources │
│  • Adaptive response │
│  • Escalation status │
└─────────────────────┘
```

---

## 🎭 Persona Detection Strategy

**Classification Method:** Zero-shot prompt classification using Google Gemini 2.5 Flash with structured JSON output (enforced schema).

**Prompt Design:** The classifier uses a carefully crafted system prompt that defines each persona with distinct behavioral markers:
- **Technical Expert**: Technical jargon, API/config/log requests, systematic problem descriptions
- **Frustrated User**: Emotional language, urgency, exclamation marks, "nothing works" phrasing
- **Business Executive**: Impact-focused, outcome-driven, SLA/timeline language, brevity preference

**Output Schema** (enforced):
```json
{
  "persona": "Technical Expert | Frustrated User | Business Executive",
  "confidence": 0.0–1.0,
  "reasoning": "explanation string"
}
```

Temperature is set to `0.1` for deterministic, consistent classification.

---

## 📚 RAG Pipeline Design

### Chunking Strategy
- **Algorithm**: `RecursiveCharacterTextSplitter` (LangChain)
- **Chunk Size**: 500 characters
- **Chunk Overlap**: 50 characters
- **Separators**: `\n\n` → `\n` → ` ` → `""` (preserves paragraph and sentence boundaries)

### Embedding Model
- **Model**: `text-embedding-001` (Google Gemini)
- **Dimensions**: 768
- **Why Gemini Embeddings**: Same provider as the LLM, optimized semantic alignment, no additional API dependency

### Vector Database
- **Database**: ChromaDB (persistent local storage)
- **Distance Metric**: Cosine similarity (`hnsw:space: cosine`)
- **Storage**: `./chroma_db/` directory (persistent — no re-indexing needed on restart)
- **Metadata stored**: source filename, chunk index, total chunks

### Retrieval Strategy
- **Top-K**: 3 most similar chunks retrieved per query
- **Score Conversion**: ChromaDB cosine distance → similarity: `score = 1.0 - (distance / 2.0)`
- **Threshold**: Chunks with score < 0.45 trigger escalation

---

## 🚨 Escalation Logic

The escalation system checks three independent triggers:

| Trigger | Condition | Threshold |
|---------|-----------|-----------|
| Low Confidence | Max similarity score of retrieved chunks | < 0.45 |
| Sensitive Topic | Keyword match in user query | billing, refund, fraud, legal, etc. |
| Repeated Frustration | Consecutive "Frustrated User" turns | ≥ 3 turns |

Escalation produces a structured handoff JSON with:
- Detected persona
- Issue summary
- Documents used
- Retrieval confidence score
- Attempted steps
- Priority level (HIGH / MEDIUM / NORMAL)
- Recommended next action

Thresholds are configurable in `src/config.py`.

---

## 📁 Project Structure

```
persona-support-agent/
│
├── data/                          # Knowledge base documents
│   ├── api_troubleshooting.md
│   ├── billing_policy.txt
│   ├── password_reset_guide.pdf   ← Required PDF
│   ├── account_management.md
│   ├── database_integration.md
│   ├── sla_uptime_policy.txt
│   ├── onboarding_guide.md
│   ├── security_faq.txt
│   ├── webhooks_guide.md
│   ├── performance_guide.txt
│   └── general_troubleshooting_faq.md
│
├── src/
│   ├── __init__.py
│   ├── config.py                  ← Thresholds, model names, settings
│   ├── classifier.py              ← Persona detection (Gemini structured output)
│   ├── rag_pipeline.py            ← Chunking, embedding, ChromaDB, retrieval
│   ├── generator.py               ← Persona-adaptive prompt builder + LLM caller
│   └── escalator.py               ← Escalation logic + handoff JSON generator
│
├── app.py                         ← Streamlit web UI
├── requirements.txt
├── .env.example                   ← Copy to .env and add your API key
├── .env                           ← NOT committed to Git
├── .gitignore
└── README.md
```

---

## ⚙️ Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/persona-support-agent.git
cd persona-support-agent
```

### 2. Create a Virtual Environment
```bash
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
```bash
cp .env.example .env
```
Open `.env` and replace the placeholder with your actual Gemini API key:
```
GEMINI_API_KEY="your_actual_gemini_api_key_here"
```
Get your key at: https://aistudio.google.com/app/apikey

### 5. Launch the Application
```bash
streamlit run app.py
```

### 6. Load the Knowledge Base
In the sidebar, click **"Load & Index Documents"**. This will:
- Parse all files in `/data/`
- Chunk and embed them using Gemini embeddings
- Store the index persistently in `./chroma_db/`

This step only needs to be done once. Subsequent sessions load the existing index.

---

## 🔑 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | ✅ Yes | Google Gemini API key from AI Studio |

---

## 💬 Example Queries

| # | Query | Expected Persona | Expected Behavior |
|---|-------|-----------------|-------------------|
| 1 | "Can you explain the 401 Unauthorized API error and show the correct Authorization header format?" | Technical Expert | Root cause analysis, code examples, header specs |
| 2 | "I've tried everything and nothing works! Your platform has been broken for hours!" | Frustrated User | Empathetic response, simple bullet steps, reassuring tone |
| 3 | "What is the operational impact of the current uptime degradation and when will SLA levels be restored?" | Business Executive | Concise, impact-focused, timeline-driven |
| 4 | "My billing statement shows duplicate charges from last month. I want a refund immediately!" | Frustrated User | **Escalated** — billing sensitivity detected, handoff JSON generated |
| 5 | "How do I configure OAuth2 bearer token auth for the REST API?" | Technical Expert | Detailed auth flow, header format, token refresh instructions |
| 6 | "The database integration is throwing internal errors on write operations." | Technical Expert | Database diagnostics, log commands, permission checks |
| 7 | "What is our current SLA and what credits do we get if it's breached?" | Business Executive | Brief SLA summary, credit policy, resolution commitment |

---

## ⚠️ Known Limitations

1. **No conversation memory across sessions**: ChromaDB persists documents but chat history resets on browser refresh. A future improvement would use SQLite to store conversation state.
2. **Single-language support**: Currently optimized for English queries only.
3. **Embedding API calls on ingestion**: First-time indexing requires one Gemini API call per chunk. Large knowledge bases may take a few minutes to index.
4. **Rate limits**: Free-tier Gemini API has rate limits. The exponential backoff handler mitigates this but very high traffic may need a paid tier.
5. **PDF text extraction**: Scanned/image-based PDFs are not supported — only PDFs with selectable text are parseable by pypdf.

### Future Improvements
- Multi-turn memory with SQLite persistence
- Sentiment analysis for more nuanced escalation
- LangGraph multi-agent workflow
- Analytics dashboard
- Support for more document formats (DOCX, HTML)
- Multilingual support

---

## 📄 License

MIT License — see LICENSE file for details.
