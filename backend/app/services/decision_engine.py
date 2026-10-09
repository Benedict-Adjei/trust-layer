"""Compatibility entry point for the authoritative policy engine."""
from app.schemas.action import AgentAction
from app.services.policy_engine import analyze


def make_decision(action: AgentAction):
    result = analyze(action)
    return {
        "decision": result.decision,
        "risk_score": result.risk_score,
        "threat_categories": result.threat_categories,
        "triggered_signals": result.triggered_signals,
        "policy_violations": result.violated_policies,
        "reasons": [result.explanation],
    }
