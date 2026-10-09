import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.audit_log import AuditLog


router = APIRouter(
    prefix="/api/audit-logs",
    tags=["Audit Logs"],
)


def serialize_log(log: AuditLog):
    return {
        "id": log.id,
        "timestamp": log.timestamp,
        "agent_name": log.agent_name,
        "user_task": log.user_task,
        "source_type": log.source_type,
        "source_trust": log.source_trust,
        "proposed_action": log.proposed_action,
        "action_target": log.action_target,
        "risk_score": log.risk_score,
        "decision": log.decision,
        "threat_categories": json.loads(log.threat_categories),
        "triggered_signals": json.loads(log.triggered_signals),
        "policy_violations": json.loads(log.policy_violations),
        "reasons": json.loads(log.reasons),
    }


@router.get("")
def get_audit_logs(db: Session = Depends(get_db)):
    logs = (
        db.query(AuditLog)
        .order_by(AuditLog.id.desc())
        .all()
    )

    return {
        "total": len(logs),
        "logs": [serialize_log(log) for log in logs],
    }


@router.get("/export")
def export_audit_logs(db: Session = Depends(get_db)):
    logs = (
        db.query(AuditLog)
        .order_by(AuditLog.id.desc())
        .all()
    )

    data = [serialize_log(log) for log in logs]

    return JSONResponse(
        content={
            "export_type": "TrustLayer Audit Log",
            "total": len(data),
            "logs": data,
        },
        headers={
            "Content-Disposition":
                'attachment; filename="trustlayer_audit_logs.json"'
        },
    )


@router.get("/{log_id}")
def get_audit_log(
    log_id: int,
    db: Session = Depends(get_db),
):
    log = (
        db.query(AuditLog)
        .filter(AuditLog.id == log_id)
        .first()
    )

    if log is None:
        raise HTTPException(
            status_code=404,
            detail="Audit log not found",
        )

    return serialize_log(log)