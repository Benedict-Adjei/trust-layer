from app.schemas.action import AgentAction
from app.services.policy_engine import check_permissions
from app.services.risk_engine import calculate_risk


def make_decision(action: AgentAction):
    # Step 1: Check what this agent is allowed to do
    permission_result = check_permissions(action)

    # Step 2: Calculate security risk
    risk_result = calculate_risk(
        action,
        forbidden_permission=permission_result["forbidden_permission"],
    )

    risk_score = risk_result["risk_score"]
    threats = risk_result["threat_categories"]

    # Default decision based on score
    if risk_score >= 70:
        decision = "BLOCK"
    elif risk_score >= 30:
        decision = "REVIEW REQUIRED"
    else:
        decision = "ALLOW"

    reasons = list(risk_result["triggered_signals"])

    # HARD OVERRIDE 1:
    # An agent attempting something outside its permissions is blocked.
    if permission_result["forbidden_permission"]:
        decision = "BLOCK"
        reasons.extend(permission_result["violations"])

    # HARD OVERRIDE 2:
    # Confidential information must not be sent to an untrusted
    # external destination.
    if (
        action.data_sensitivity.lower() == "confidential"
        and action.requires_external_communication
        and action.source_trust.lower() == "untrusted"
    ):
        decision = "BLOCK"
        reasons.append(
            "Confidential data cannot be transmitted from an "
            "untrusted external request."
        )

    # HARD OVERRIDE 3:
    # Payments must never be automatically allowed.
    if action.requires_payment and decision == "ALLOW":
        decision = "REVIEW REQUIRED"
        reasons.append(
            "Payment actions require human verification."
        )

    return {
        "decision": decision,
        "risk_score": risk_score,
        "threat_categories": threats,
        "triggered_signals": risk_result["triggered_signals"],
        "policy_violations": permission_result["violations"],
        "reasons": list(dict.fromkeys(reasons)),
    }