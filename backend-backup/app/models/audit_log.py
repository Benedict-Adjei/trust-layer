from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    timestamp = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    agent_name = Column(String, nullable=False)
    user_task = Column(Text, nullable=False)

    source_type = Column(String, nullable=False)
    source_trust = Column(String, nullable=False)

    proposed_action = Column(String, nullable=False)
    action_target = Column(String, nullable=True)

    risk_score = Column(Integer, nullable=False)
    decision = Column(String, nullable=False)

    threat_categories = Column(Text, nullable=False, default="[]")
    triggered_signals = Column(Text, nullable=False, default="[]")
    policy_violations = Column(Text, nullable=False, default="[]")
    reasons = Column(Text, nullable=False, default="[]")