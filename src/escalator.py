# src/escalator.py
# ─────────────────────────────────────────────
# Escalation decision engine + handoff JSON generator
# ─────────────────────────────────────────────

import json
from src.config import (
    CONFIDENCE_THRESHOLD, SENSITIVE_KEYWORDS, MAX_FRUSTRATED_TURNS
)


def check_escalation(
    user_query: str,
    persona: str,
    context_chunks: list[dict],
    conversation_history: list[dict]
) -> dict:
    """
    Evaluates whether the current query should be escalated to a human agent.

    Returns:
        {
            "should_escalate": bool,
            "reason": str
        }
    """
    # Trigger 1: Low retrieval confidence
    if not context_chunks:
        return {
            "should_escalate": True,
            "reason": "no_context_found"
        }

    best_score = max(c["score"] for c in context_chunks)
    if best_score < CONFIDENCE_THRESHOLD:
        return {
            "should_escalate": True,
            "reason": f"low_confidence (score={best_score:.2f}, threshold={CONFIDENCE_THRESHOLD})"
        }

    # Trigger 2: Sensitive topic keywords
    query_lower = user_query.lower()
    for keyword in SENSITIVE_KEYWORDS:
        if keyword in query_lower:
            return {
                "should_escalate": True,
                "reason": f"sensitive_topic_detected (keyword='{keyword}')"
            }

    # Trigger 3: Repeated frustration over consecutive turns
    if persona == "Frustrated User":
        recent_frustrated = sum(
            1 for turn in conversation_history[-MAX_FRUSTRATED_TURNS:]
            if turn.get("persona") == "Frustrated User"
        )
        if recent_frustrated >= MAX_FRUSTRATED_TURNS:
            return {
                "should_escalate": True,
                "reason": f"repeated_frustration ({recent_frustrated} consecutive frustrated turns)"
            }

    return {"should_escalate": False, "reason": None}


def generate_handoff_summary(
    user_query: str,
    persona: str,
    context_chunks: list[dict],
    conversation_history: list[dict],
    escalation_reason: str
) -> str:
    """
    Generates a structured JSON handoff report for the human support agent.
    """
    # Reconstruct attempted steps from conversation history
    attempted_steps = []
    for turn in conversation_history:
        if turn.get("role") == "assistant" and not turn.get("escalated"):
            attempted_steps.append(turn.get("response_summary", "Provided automated response"))

    # Sources used
    sources_used = list({c["source"] for c in context_chunks}) if context_chunks else []

    # Best confidence score
    best_score = max((c["score"] for c in context_chunks), default=0.0)

    # Recommended action based on reason
    recommendation_map = {
        "no_context_found": "Issue is outside the knowledge base. Manual investigation required.",
        "sensitive_topic_detected": "Billing/legal/account issue — requires authorized human agent review.",
        "repeated_frustration": "Customer is highly frustrated after multiple interactions. Prioritize empathy and fast resolution.",
    }
    recommendation = next(
        (v for k, v in recommendation_map.items() if k in escalation_reason),
        "Review conversation history and resolve with appropriate team."
    )

    handoff_data = {
        "persona": persona,
        "issue": user_query[:200] + ("..." if len(user_query) > 200 else ""),
        "escalation_reason": escalation_reason,
        "documents_used": sources_used,
        "retrieval_confidence_score": round(best_score, 4),
        "attempted_steps": attempted_steps if attempted_steps else ["No prior steps taken — first interaction"],
        "conversation_turns": len(conversation_history),
        "recommendation": recommendation,
        "priority": _assess_priority(persona, escalation_reason)
    }

    return json.dumps(handoff_data, indent=2)


def _assess_priority(persona: str, reason: str) -> str:
    """Assigns a priority level to the escalated ticket."""
    if "billing" in reason or "legal" in reason or "fraud" in reason:
        return "HIGH"
    if persona == "Frustrated User" and "repeated" in reason:
        return "HIGH"
    if persona == "Business Executive":
        return "MEDIUM"
    return "NORMAL"
