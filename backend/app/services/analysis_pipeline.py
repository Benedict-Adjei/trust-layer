"""Compose optional evidence with the unchanged authoritative policy result."""
from app.services.policy_engine import analyze


async def analyze_proposal(action, contextual_analyzer, include_contextual=False):
    deterministic = analyze(action)
    if not include_contextual:
        return deterministic
    assessment = await contextual_analyzer.analyze(action, deterministic)
    # Only the evidence field is attached. No LLM value can alter any verdict,
    # risk score, policy, signal, explanation or recommended deterministic step.
    return deterministic.model_copy(update={"contextual_analysis": assessment})
