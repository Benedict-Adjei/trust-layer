from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, Field


class AgentAction(BaseModel):
    agent_name: str
    user_task: str

    source_type: str
    source_trust: str

    external_content: str

    proposed_action: str
    action_target: Optional[str] = None

    requested_resources: List[str] = Field(default_factory=list)

    data_sensitivity: str = "public"

    requires_external_communication: bool = False
    requires_payment: bool = False
    user_approved: bool = False

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )