# app.py
# ─────────────────────────────────────────────
# Persona-Adaptive Customer Support Agent
# Streamlit Web UI — Main Entry Point
# ─────────────────────────────────────────────

import streamlit as st
import json
import time

from src.classifier import classify_customer_persona
from src.rag_pipeline import LocalRAGPipeline
from src.generator import generate_adaptive_response
from src.escalator import check_escalation, generate_handoff_summary

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Persona-Adaptive Support Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .persona-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 4px 0;
    }
    .tech { background: #dbeafe; color: #1e40af; }
    .frustrated { background: #fee2e2; color: #991b1b; }
    .exec { background: #d1fae5; color: #065f46; }
    .escalated { background: #fef3c7; color: #92400e; }
    .source-chip {
        display: inline-block;
        background: #f3f4f6;
        color: #374151;
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 0.75rem;
        margin: 2px;
    }
    .confidence-bar {
        height: 6px;
        border-radius: 3px;
        background: linear-gradient(90deg, #10b981, #3b82f6);
    }
    .handoff-box {
        background: #fffbeb;
        border-left: 4px solid #f59e0b;
        padding: 12px;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)


# ── Session State Initialization ──────────────────────────────────────────────
def init_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []         # chat history shown in UI
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []   # for escalation tracking
    if "rag" not in st.session_state:
        st.session_state.rag = None
    if "kb_loaded" not in st.session_state:
        st.session_state.kb_loaded = False
    if "kb_summary" not in st.session_state:
        st.session_state.kb_summary = {}

init_session()


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Control Panel")
    st.markdown("---")

    # Knowledge Base section
    st.subheader("📚 Knowledge Base")

    if not st.session_state.kb_loaded:
        if st.button("🔄 Load & Index Documents", use_container_width=True, type="primary"):
            with st.spinner("Ingesting documents into ChromaDB..."):
                try:
                    rag = LocalRAGPipeline()
                    summary = rag.ingest_all_documents()
                    st.session_state.rag = rag
                    st.session_state.kb_summary = summary
                    st.session_state.kb_loaded = True
                    st.success(f"✅ Indexed {sum(summary.values())} chunks from {len(summary)} documents!")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
    else:
        stats = st.session_state.rag.get_collection_stats()
        st.success(f"✅ KB Ready — {stats['total_chunks']} chunks indexed")

        with st.expander("📄 Indexed Documents"):
            for doc, chunks in st.session_state.kb_summary.items():
                st.markdown(f"- **{doc}** → {chunks} chunks")

        if st.button("🔁 Re-index Documents", use_container_width=True):
            st.session_state.kb_loaded = False
            st.session_state.rag = None
            st.rerun()

    st.markdown("---")

    # Persona legend
    st.subheader("🎭 Persona Guide")
    st.markdown("""
    <span class="persona-badge tech">🔧 Technical Expert</span><br>
    Uses technical jargon, asks about APIs/logs/configs<br><br>
    <span class="persona-badge frustrated">😤 Frustrated User</span><br>
    Emotional language, urgency, repeated complaints<br><br>
    <span class="persona-badge exec">💼 Business Executive</span><br>
    Outcome-focused, wants timelines & impact summaries
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Example queries
    st.subheader("💡 Example Queries")
    examples = [
        "Can you explain the API 401 Unauthorized error and show the correct auth headers?",
        "I've tried everything and nothing works! Your platform is terrible!",
        "What is the business impact of the current outage and when will it be resolved?",
        "My billing statement has unexpected duplicate charges. I demand a refund!",
        "How do I configure OAuth2 bearer token authentication for your REST API?",
    ]
    for ex in examples:
        if st.button(ex[:55] + "...", key=ex, use_container_width=True):
            st.session_state["prefill"] = ex

    st.markdown("---")

    # Clear chat
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.conversation_history = []
        st.rerun()


# ── Main Area ─────────────────────────────────────────────────────────────────
st.title("🤖 Persona-Adaptive Customer Support Agent")
st.caption("Powered by Google Gemini · LangChain RAG · ChromaDB")

if not st.session_state.kb_loaded:
    st.info("👈 Please click **Load & Index Documents** in the sidebar to initialize the knowledge base before chatting.")

# Render existing chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "user":
            st.markdown(msg["content"])
        else:
            # Persona badge
            persona = msg.get("persona", "")
            badge_class = {"Technical Expert": "tech", "Frustrated User": "frustrated", "Business Executive": "exec"}.get(persona, "tech")
            st.markdown(
                f'<span class="persona-badge {badge_class}">🎭 Detected Persona: {persona}</span>'
                f' &nbsp; <span style="font-size:0.8rem; color:#6b7280;">Confidence: {msg.get("confidence", 0):.0%}</span>',
                unsafe_allow_html=True
            )

            # Escalation notice
            if msg.get("escalated"):
                st.markdown(
                    f'<div class="handoff-box">⚠️ <strong>ESCALATED TO HUMAN AGENT</strong><br>'
                    f'<small>Reason: {msg.get("escalation_reason", "N/A")}</small></div>',
                    unsafe_allow_html=True
                )

            # Response
            st.markdown(msg["content"])

            # Sources
            sources = msg.get("sources", [])
            if sources:
                st.markdown("**📎 Retrieved Sources:**")
                for src in sources:
                    st.markdown(
                        f'<span class="source-chip">📄 {src["source"]} (score: {src["score"]:.2f})</span>',
                        unsafe_allow_html=True
                    )

            # Handoff JSON
            if msg.get("handoff_json"):
                with st.expander("📋 Human Handoff Summary (JSON)"):
                    st.code(msg["handoff_json"], language="json")


# ── Chat Input ────────────────────────────────────────────────────────────────
prefill = st.session_state.pop("prefill", "")
user_input = st.chat_input("Type your support query here...", key="chat_input") or prefill

if user_input and st.session_state.kb_loaded:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Process
    with st.chat_message("assistant"):
        with st.spinner("Analyzing your message..."):

            # Step 1: Persona Classification
            try:
                persona_result = classify_customer_persona(user_input)
                persona = persona_result["persona"]
                confidence = persona_result["confidence"]
                reasoning = persona_result["reasoning"]
            except Exception as e:
                persona, confidence, reasoning = "Frustrated User", 0.5, str(e)

            # Step 2: RAG Retrieval
            try:
                context_chunks = st.session_state.rag.retrieve_context(user_input)
            except Exception as e:
                context_chunks = []

            # Step 3: Escalation Check
            escalation = check_escalation(
                user_input, persona, context_chunks,
                st.session_state.conversation_history
            )

            handoff_json = None
            escalated = escalation["should_escalate"]
            escalation_reason = escalation.get("reason", "")

            if escalated:
                handoff_json = generate_handoff_summary(
                    user_input, persona, context_chunks,
                    st.session_state.conversation_history,
                    escalation_reason
                )
                response_text = (
                    "I sincerely apologize, but I'm unable to fully resolve this through automated support. "
                    "I'm immediately connecting you with a specialized human support agent who can assist you properly.\n\n"
                    "A detailed handoff summary has been prepared for the agent below."
                )
            else:
                # Step 4: Generate Adaptive Response
                try:
                    response_text = generate_adaptive_response(user_input, persona, context_chunks)
                except Exception as e:
                    response_text = f"I encountered an error generating a response: {e}"

        # ── Render Response ────────────────────────────────────────────────
        badge_class = {"Technical Expert": "tech", "Frustrated User": "frustrated", "Business Executive": "exec"}.get(persona, "tech")
        st.markdown(
            f'<span class="persona-badge {badge_class}">🎭 Detected Persona: {persona}</span>'
            f' &nbsp; <span style="font-size:0.8rem; color:#6b7280;">Confidence: {confidence:.0%} · {reasoning[:80]}...</span>',
            unsafe_allow_html=True
        )

        if escalated:
            st.markdown(
                f'<div class="handoff-box">⚠️ <strong>ESCALATED TO HUMAN AGENT</strong><br>'
                f'<small>Reason: {escalation_reason}</small></div>',
                unsafe_allow_html=True
            )

        st.markdown(response_text)

        # Sources
        if context_chunks:
            st.markdown("**📎 Retrieved Sources:**")
            for src in context_chunks:
                st.markdown(
                    f'<span class="source-chip">📄 {src["source"]} (score: {src["score"]:.2f})</span>',
                    unsafe_allow_html=True
                )

        # Handoff JSON
        if handoff_json:
            with st.expander("📋 Human Handoff Summary (JSON)"):
                st.code(handoff_json, language="json")

    # ── Save to session state ─────────────────────────────────────────────
    st.session_state.messages.append({
        "role": "assistant",
        "content": response_text,
        "persona": persona,
        "confidence": confidence,
        "escalated": escalated,
        "escalation_reason": escalation_reason,
        "sources": context_chunks,
        "handoff_json": handoff_json
    })

    st.session_state.conversation_history.append({
        "role": "assistant",
        "persona": persona,
        "escalated": escalated,
        "response_summary": response_text[:100]
    })

elif user_input and not st.session_state.kb_loaded:
    st.warning("⚠️ Please load the knowledge base first using the sidebar button.")
