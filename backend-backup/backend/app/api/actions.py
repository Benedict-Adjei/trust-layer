<<<<<<< HEAD
import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.audit_log import AuditLog
from app.schemas.action import AgentAction
from app.services.decision_engine import make_decision


router = APIRouter(
    prefix="/api/actions",
    tags=["Actions"],
)


@router.post("/analyze")
def analyze_action(
    action: AgentAction,
    db: Session = Depends(get_db),
):
    # Analyze the proposed AI-agent action
    result = make_decision(action)

    # Create an audit record
    audit_log = AuditLog(
        agent_name=action.agent_name,
        user_task=action.user_task,
        source_type=action.source_type,
        source_trust=action.source_trust,
        proposed_action=action.proposed_action,
        action_target=action.action_target,
        risk_score=result["risk_score"],
        decision=result["decision"],
        threat_categories=json.dumps(
            result["threat_categories"]
        ),
        triggered_signals=json.dumps(
            result["triggered_signals"]
        ),
        policy_violations=json.dumps(
            result["policy_violations"]
        ),
        reasons=json.dumps(
            result["reasons"]
        ),
    )

    # Save the security decision
    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)

    # Return the analysis to the caller
    return {
        "audit_log_id": audit_log.id,
        "agent": action.agent_name,
        "proposed_action": action.proposed_action,
        "action_target": action.action_target,
        **result,
    }
=======
from fastapi import APIRouter, Request

from app.schemas.action import AgentAction, AnalysisResult
from app.services.analysis_pipeline import analyze_proposal
from starlette.concurrency import run_in_threadpool

router = APIRouter(prefix="/api/actions", tags=["Actions"])


@router.post("/analyze", response_model=AnalysisResult, response_model_exclude_none=True)
async def analyze_action(action: AgentAction, request: Request, contextual: bool = False):
    result = await analyze_proposal(action, request.app.state.contextual_analyzer, contextual)
    # Fail the request if durable logging fails; never claim unrecorded success.
    await run_in_threadpool(request.app.state.database.record, action, result)
    return result
>>>>>>> 5ed4fa365817236328cfeade0b6d269d2df33f60
