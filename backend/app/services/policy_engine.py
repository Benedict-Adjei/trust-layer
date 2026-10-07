from uuid import uuid4

from app.schemas.action import AnalysisResult
from app.services.agent_permissions import get_profile
from app.services.risk_engine import action_effects, evaluate_risk

POLICIES = [
    {"id": "known_agent", "description": "Only registered permission profiles may propose actions."},
    {"id": "action_scope", "description": "Actions must belong to the agent's allowed action set."},
    {"id": "resource_scope", "description": "Requested resources must be explicitly permitted by the profile."},
    {"id": "no_prompt_injection", "description": "Instruction overrides, authority spoofing and concealment require blocking."},
    {"id": "no_sensitive_exfiltration", "description": "Confidential or restricted external transfers are blocked even with approval."},
    {"id": "side_effect_approval", "description": "External communications and payments require explicit user approval."},
    {"id": "target_required", "description": "External communications and payments require a destination."},
    {"id": "risk_threshold", "description": "Scores below 30 allow, 30–69 require review, and 70–100 block."},
]


def analyze(action):
    risk = evaluate_risk(action)
    external, payment = action_effects(action)
    profile = get_profile(action.agent_name)
    violations = []
    hard_block = False

    def violate(policy, category, signal, hard=True):
        nonlocal hard_block
        violations.append(policy)
        if category not in risk["categories"]:
            risk["categories"].append(category)
        if signal not in risk["signals"]:
            risk["signals"].append(signal)
        hard_block |= hard

    if profile is None:
        violate("known_agent", "permission_violation", "unknown_agent")
    else:
        if action.proposed_action not in profile["allowed_actions"]:
            violate("action_scope", "permission_violation", "action_outside_profile")
        if any(resource not in profile["allowed_resources"] for resource in action.requested_resources):
            violate("resource_scope", "permission_violation", "resource_outside_profile")
    if "prompt_injection" in risk["categories"]:
        violate("no_prompt_injection", "prompt_injection", "injection_policy_triggered")
    if external and action.data_sensitivity in {"confidential", "restricted"}:
        violate("no_sensitive_exfiltration", "data_exfiltration", "sensitive_external_transfer")
    needs_approval = external or payment or (profile and action.proposed_action in profile["approval_actions"])
    if needs_approval and not action.explicit_user_approval:
        violate("side_effect_approval", "unauthorized_action", "explicit_approval_missing", hard=False)
    if (external or payment) and not action.action_target:
        violate("target_required", "unauthorized_action", "destination_missing")
    score = max(risk["score"], 70 if hard_block else 30 if violations else 0)
    decision = "BLOCK" if hard_block or score >= 70 else "REVIEW REQUIRED" if score >= 30 else "ALLOW"
    if score >= 30:
        violations.append("risk_threshold")
    level = "critical" if score >= 90 else "high" if score >= 70 else "medium" if score >= 30 else "low"
    reason = ", ".join(risk["signals"]) or "no suspicious signals; action and resources match the agent profile"
    next_step = {
        "ALLOW": "The proposed action passed deterministic checks. This API records analysis only and does not execute actions.",
        "REVIEW REQUIRED": "Obtain human approval and verify the destination and task scope, then submit a new analysis.",
        "BLOCK": "Stop the proposed action. Remove injected instructions or prohibited access and submit a safe action for analysis.",
    }[decision]
    return AnalysisResult(
        action_id=str(uuid4()), decision=decision, risk_score=score, risk_level=level,
        threat_categories=risk["categories"], triggered_signals=risk["signals"],
        violated_policies=violations, explanation=f"{decision}: {reason}." + (f" Policies: {', '.join(violations)}." if violations else ""),
        recommended_next_step=next_step,
    )
