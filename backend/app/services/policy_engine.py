from app.schemas.action import AgentAction


AGENT_POLICIES = {
    "Email Assistant": {
        "allowed_actions": [
            "read_email",
            "summarize_email",
            "draft_email",
            "send_email",
        ],
        "allowed_resources": [
            "email",
            "contacts",
        ],
    },

    "Research Assistant": {
        "allowed_actions": [
            "web_search",
            "read_document",
            "summarize_document",
            "create_report",
        ],
        "allowed_resources": [
            "web",
            "documents",
        ],
    },

    "Finance Assistant": {
        "allowed_actions": [
            "read_invoice",
            "verify_payment",
            "prepare_payment",
        ],
        "allowed_resources": [
            "invoices",
            "payment_records",
        ],
    },
}


def check_permissions(action: AgentAction):
    policy = AGENT_POLICIES.get(action.agent_name)

    # Unknown agents are not trusted automatically.
    if policy is None:
        return {
            "forbidden_permission": True,
            "violations": [
                f"Unknown agent: {action.agent_name}"
            ],
        }

    violations = []

    # Check proposed action
    if action.proposed_action not in policy["allowed_actions"]:
        violations.append(
            f"{action.agent_name} is not allowed to perform "
            f"{action.proposed_action}"
        )

    # Check every requested resource
    for resource in action.requested_resources:
        if resource not in policy["allowed_resources"]:
            violations.append(
                f"{action.agent_name} is not allowed to access "
                f"{resource}"
            )

    return {
        "forbidden_permission": len(violations) > 0,
        "violations": violations,
    }