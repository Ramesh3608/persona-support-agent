# src/generator.py
# ─────────────────────────────────────────────
# Persona-adaptive prompt builder + LLM response generator
# ─────────────────────────────────────────────

import time
import random
from google import genai
from google.genai import types
from src.config import GEMINI_API_KEY, LLM_MODEL


# ── Persona System Prompts ────────────────────────────────────────────────────

PERSONA_PROMPTS = {
    "Technical Expert": (
        "You are a Senior Systems Engineer providing expert-level technical support. "
        "Your responses must:\n"
        "- Begin with a clear root-cause analysis of the issue\n"
        "- Include precise configuration specifications, API endpoints, or code blocks where relevant\n"
        "- Provide numbered step-by-step troubleshooting instructions\n"
        "- Use correct technical terminology throughout\n"
        "- Mention relevant log paths, error codes, or diagnostic commands\n"
        "- Be structured and detailed without unnecessary filler"
    ),
    "Frustrated User": (
        "You are a deeply empathetic and reassuring Customer Care Specialist. "
        "Your responses must:\n"
        "- Begin with a warm, genuine validation of their frustration (e.g., 'I completely understand how frustrating this is...')\n"
        "- Use simple, clear, jargon-free language\n"
        "- Break down resolution steps into short, easy bullet points\n"
        "- Be reassuring and action-oriented throughout\n"
        "- Avoid lengthy technical explanations\n"
        "- End with a supportive closing line"
    ),
    "Business Executive": (
        "You are a concise Client Relations Director communicating with a C-suite executive. "
        "Your responses must:\n"
        "- Lead with the bottom-line answer immediately\n"
        "- Include operational impact and estimated resolution timeline\n"
        "- Be extremely brief and professional (3-5 sentences max)\n"
        "- Skip technical implementation details entirely\n"
        "- Use business language: SLAs, uptime, impact, resolution ETA\n"
        "- Close with a commitment statement"
    )
}


def generate_adaptive_response(
    user_query: str,
    persona: str,
    context_chunks: list[dict]
) -> str:
    """
    Builds a persona-specific system prompt, injects retrieved context,
    and calls the Gemini LLM to generate a grounded response.

    Responses are strictly grounded in retrieved documents — no hallucination.
    """
    client = genai.Client(api_key=GEMINI_API_KEY)

    # Select persona-specific instructions
    persona_instructions = PERSONA_PROMPTS.get(persona, PERSONA_PROMPTS["Frustrated User"])

    # Build context block from retrieved chunks
    context_text = ""
    for i, chunk in enumerate(context_chunks):
        context_text += (
            f"\n--- Document {i+1}: [{chunk['source']}] "
            f"(relevance score: {chunk['score']:.2f}) ---\n"
            f"{chunk['text']}\n"
        )

    # Full system prompt
    full_system_prompt = (
        f"{persona_instructions}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "CRITICAL RULES (Non-negotiable):\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "1. Base your response ONLY on the FACTUAL CONTEXT DOCUMENTS provided below.\n"
        "2. Do NOT hallucinate, invent, or assume any facts not present in the documents.\n"
        "3. If the documents do not contain a clear answer, honestly say so.\n"
        "4. Always match your tone and format to the persona instructions above.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "FACTUAL CONTEXT DOCUMENTS:\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        f"{context_text}"
    )

    response = _call_with_backoff(
        client.models.generate_content,
        model=LLM_MODEL,
        contents=user_query,
        config=types.GenerateContentConfig(
            system_instruction=full_system_prompt,
            temperature=0.2,
            max_output_tokens=1024
        )
    )

    return response.text


def _call_with_backoff(func, *args, max_retries: int = 5, **kwargs):
    """Exponential backoff wrapper for resilient Gemini API calls."""
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            sleep_time = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(sleep_time)
