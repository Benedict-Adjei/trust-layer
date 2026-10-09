"""The persisted, redacted audit record returned by the API."""
from datetime import datetime
from typing import Any

from pydantic import BaseModel

from app.schemas.action import AnalysisResult


class AuditLog(BaseModel):
    action_id: str
    created_at: datetime
    action: dict[str, Any]
    result: AnalysisResult
