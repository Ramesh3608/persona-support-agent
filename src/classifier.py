# src/classifier.py
# ─────────────────────────────────────────────
# Detects customer persona from incoming message
# using Gemini structured JSON output
# ─────────────────────────────────────────────

import json
import time
import random
from google import genai
from google.genai import types
from src.config import GEMINI_API_KEY, LLM_MODEL


def classify_customer_persona(user_message: str) -> dict:
    """
    Classifies the incoming user message into one of three personas:
    - Technical Expert
    - Frustrated User
    - Business Executive

    Returns a dict: { persona, confidence, reasoning }
    """
    client = genai.Client(api_key=GEMINI_API_KEY)

    system_instruction = (
        "You are an advanced classification engine. Your task is to analyze the "
        "sentiment, vocabulary, and tone of an incoming support message and classify "
        "it into exactly one of three customer personas:\n\n"
        "1. 'Technical Expert': Uses technical jargon, asks about APIs, code, configs, "
        "logs, error codes, or system architecture. Requests detailed explanations.\n"
        "2. 'Frustrated User': Uses emotional language, exclamation marks, expresses "
        "urgency or desperation, repeats complaints, says things like 'nothing works' "
        "or 'I've tried everything'.\n"
        "3. 'Business Executive': Focuses on business impact, ROI, timelines, SLAs, "
        "operational outcomes. Prefers concise, outcome-driven communication.\n\n"
        "Provide your evaluation STRICTLY in the requested JSON structure. "
        "confidence must be a float between 0.0 and 1.0."
    )

    response_schema = {
        "type": "OBJECT",
        "properties": {
            "persona": {
                "type": "STRING",
                "enum": ["Technical Expert", "Frustrated User", "Business Executive"]
            },
            "confidence": {"type": "NUMBER"},
            "reasoning": {"type": "STRING"}
        },
        "required": ["persona", "confidence", "reasoning"]
    }

    result = _call_with_backoff(
        client.models.generate_content,
        model=LLM_MODEL,
        contents=user_message,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=response_schema,
            temperature=0.1
        )
    )

    return json.loads(result.text)


def _call_with_backoff(func, *args, max_retries: int = 5, **kwargs):
    """Exponential backoff wrapper for Gemini API calls."""
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            sleep_time = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(sleep_time)
