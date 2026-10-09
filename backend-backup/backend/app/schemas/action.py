<<<<<<< HEAD
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
=======
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictBool
from app.schemas.contextual import ContextualAnalysis


class AgentAction(BaseModel):
    """A proposed action; this API never executes it."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    agent_name: str = Field(min_length=1, max_length=100)
    user_task: str = Field(min_length=1, max_length=10000)
    source_type: str = Field(min_length=1, max_length=100)
    source_trust: Literal["trusted", "untrusted", "unknown"]
    external_content: str = Field(max_length=50000)
    proposed_action: str = Field(min_length=1, max_length=100)
    action_target: str | None = Field(default=None, max_length=2000)
    requested_resources: list[str] = Field(default_factory=list, max_length=100)
    data_sensitivity: Literal["public", "internal", "confidential", "restricted"]
    requires_external_communication: StrictBool = False
    requires_payment: StrictBool = False
    explicit_user_approval: StrictBool = False


class AnalysisResult(BaseModel):
    action_id: str
    decision: Literal["ALLOW", "REVIEW REQUIRED", "BLOCK"]
    risk_score: int = Field(ge=0, le=100)
    risk_level: Literal["low", "medium", "high", "critical"]
    threat_categories: list[str]
    triggered_signals: list[str]
    violated_policies: list[str]
    explanation: str
    recommended_next_step: str
    contextual_analysis: ContextualAnalysis | None = None
>>>>>>> 5ed4fa365817236328cfeade0b6d269d2df33f60
