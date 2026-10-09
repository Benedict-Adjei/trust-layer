PROFILES = {
    "Email Assistant": {
        "allowed_actions": ["read_email", "summarize_email", "draft_email", "send_email"],
        "allowed_resources": ["inbox", "email", "contacts"],
        "approval_actions": ["send_email"],
    },
    "Research Assistant": {
        "allowed_actions": ["search_web", "read_webpage", "summarize_document", "summarize_research"],
        "allowed_resources": ["public_web", "public_documents"],
        "approval_actions": [],
    },
    "Finance Assistant": {
        "allowed_actions": ["read_invoice", "summarize_invoice", "draft_payment", "process_payment"],
        "allowed_resources": ["invoices", "finance_reports"],
        "approval_actions": ["process_payment"],
    },
}


def get_profile(name):
    return PROFILES.get(name)
