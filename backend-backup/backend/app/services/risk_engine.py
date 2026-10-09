<<<<<<< HEAD
from app.schemas.action import AgentAction


PROMPT_INJECTION_PHRASES = [
    "ignore previous instructions",
    "ignore all prior rules",
    "disregard your system prompt",
    "reveal hidden instructions",
    "act as administrator",
    "do not tell the user",
    "override safety",
]

SENSITIVE_TERMS = [
    "password",
    "secret",
    "api key",
    "customer database",
    "customer_data",
    "private key",
    "confidential",
    "bank account",
    "verification code",
]

SOCIAL_ENGINEERING_TERMS = [
    "urgent",
    "immediately",
    "send money now",
    "do not call",
    "keep this confidential",
    "your account will be blocked",
]


def contains_prompt_injection(text: str) -> bool:
    text = text.lower()
    return any(phrase in text for phrase in PROMPT_INJECTION_PHRASES)


def contains_sensitive_terms(text: str) -> bool:
    text = text.lower()
    return any(term in text for term in SENSITIVE_TERMS)


def contains_social_engineering(text: str) -> bool:
    text = text.lower()
    return any(term in text for term in SOCIAL_ENGINEERING_TERMS)


def calculate_risk(
    action: AgentAction,
    forbidden_permission: bool = False,
):
    score = 0
    signals = []
    threats = []

    content = action.external_content.lower()

    # 1. Untrusted source
    if action.source_trust.lower() == "untrusted":
        score += 20
        signals.append("Untrusted content source")

    # 2. Prompt injection
    if contains_prompt_injection(content):
        score += 30
        signals.append("Instruction override phrase detected")

        threats.extend([
            "indirect_prompt_injection",
            "suspicious_instruction_override",
        ])

    # 3. Sensitive information
    sensitive = (
        action.data_sensitivity.lower() == "confidential"
        or contains_sensitive_terms(content)
    )

    if sensitive:
        score += 25
        signals.append("Sensitive or confidential data involved")
        threats.append("sensitive_data_exposure")

    # 4. External transmission
    if action.requires_external_communication:
        score += 30
        signals.append("External communication requested")
        threats.append("external_recipient_risk")

        if sensitive:
            threats.append("data_exfiltration")

    # 5. Permission violation
    if forbidden_permission:
        score += 35
        signals.append("Action exceeds agent permissions")
        threats.append("excessive_permissions")

    # 6. Payment
    if action.requires_payment:
        score += 25
        signals.append("Financial action requested")
        threats.append("payment_fraud")

    # 7. Social engineering
    if contains_social_engineering(content):
        score += 15
        signals.append("Urgency or secrecy language detected")
        threats.append("phishing_or_social_engineering")

    # 8. Explicit user approval
    if action.user_approved:
        score -= 20
        signals.append("User explicitly approved the action")

    # 9. Low-risk trusted internal action
    if (
        action.source_trust.lower() == "trusted"
        and action.data_sensitivity.lower() == "public"
        and not action.requires_external_communication
        and not action.requires_payment
    ):
        score -= 10

    # Risk must stay between 0 and 100
    score = max(0, min(score, 100))

    return {
        "risk_score": score,
        "triggered_signals": list(dict.fromkeys(signals)),
        "threat_categories": list(dict.fromkeys(threats)),
    }
=======
import re
import unicodedata

from app.schemas.action import AgentAction

EXTERNAL_ACTIONS = {"send_email", "send_message", "upload_file", "export_data", "share_file", "post_webhook"}
PAYMENT_ACTIONS = {"process_payment", "execute_payment", "transfer_funds", "pay_invoice"}


def action_effects(action: AgentAction):
    # Infer effects from the operation as well as caller flags.
    return (
        action.requires_external_communication or action.proposed_action in EXTERNAL_ACTIONS,
        action.requires_payment or action.proposed_action in PAYMENT_ACTIONS,
    )


def evaluate_risk(action: AgentAction):
    content = unicodedata.normalize("NFKC", action.external_content).casefold()
    content = re.sub(r"[\u200b-\u200f\ufeff]", "", content)
    external, payment = action_effects(action)
    signals = []
    categories = []
    score = 0

    def signal(name, category, weight):
        nonlocal score
        signals.append(name)
        if category not in categories:
            categories.append(category)
        score += weight

    if re.search(r"\b(ignore|disregard|override|forget)\b.{0,60}\b(instructions?|rules?|polic(?:y|ies)|system)\b", content):
        signal("instruction_override", "prompt_injection", 40)
    if re.search(r"do not (tell|inform)|don't (tell|inform)|hide (this|the)|keep.{0,20}secret|silently|without.{0,20}(approval|permission)", content):
        signal("concealment_or_approval_bypass", "prompt_injection", 30)
    if re.search(r"system (message|override)|developer (message|instruction)|administrator.{0,20}(requires|instructs)|you are now", content):
        signal("authority_spoofing", "prompt_injection", 35)
    if action.source_trust != "trusted" and re.search(r"\b(send|upload|forward|export|transfer)\b.{0,100}\b(data|files?|csv|credentials?|secrets?|tokens?|passwords?)\b", content):
        signal("untrusted_data_transfer_instruction", "data_exfiltration", 40)
    if external and action.data_sensitivity in {"confidential", "restricted"}:
        signal("sensitive_external_transfer", "data_exfiltration", 70)
    if external and not action.explicit_user_approval:
        signal("unapproved_external_communication", "unauthorized_action", 30)
    if payment and not action.explicit_user_approval:
        signal("unapproved_payment", "financial_risk", 60)
    if action.source_trust != "trusted" and (external or payment):
        signal("untrusted_source_side_effect", "task_hijacking", 25)
    return {"score": min(score, 100), "signals": signals, "categories": categories}
>>>>>>> 5ed4fa365817236328cfeade0b6d269d2df33f60
