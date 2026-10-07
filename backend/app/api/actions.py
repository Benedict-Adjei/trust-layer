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
