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
