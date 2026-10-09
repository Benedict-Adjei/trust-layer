from typing import Literal

from fastapi import APIRouter, HTTPException, Query, Request

from app.schemas.action import AgentAction, AnalysisResult
from app.services.analysis_pipeline import analyze_proposal
from starlette.concurrency import run_in_threadpool

router = APIRouter(prefix="/api", tags=["Catalog and Audit"])


def lookup(request, table, identifier):
    item = request.app.state.database.catalog(table, identifier)
    if item is None:
        raise HTTPException(status_code=404, detail=f"{table}: item not found")
    return item


@router.get("/agents")
def agents(request: Request):
    return request.app.state.database.catalog("agents")


@router.get("/agents/{agent_name}")
def agent(agent_name: str, request: Request):
    return lookup(request, "agents", agent_name)


@router.get("/policies")
def policies(request: Request):
    return request.app.state.database.catalog("policies")


@router.get("/policies/{policy_id}")
def policy(policy_id: str, request: Request):
    return lookup(request, "policies", policy_id)


@router.get("/scenarios")
def scenarios(request: Request):
    return request.app.state.database.catalog("scenarios")


@router.get("/scenarios/{scenario_id}")
def scenario(scenario_id: str, request: Request):
    return lookup(request, "scenarios", scenario_id)


@router.post("/scenarios/{scenario_id}/analyze", response_model=AnalysisResult, response_model_exclude_none=True)
async def analyze_scenario(scenario_id: str, request: Request, contextual: bool = False):
    action = AgentAction.model_validate(lookup(request, "scenarios", scenario_id)["action"])
    result = await analyze_proposal(action, request.app.state.contextual_analyzer, contextual)
    await run_in_threadpool(request.app.state.database.record, action, result)
    return result


@router.get("/audit")
def audit(request: Request, limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0),
          decision: Literal["ALLOW", "REVIEW REQUIRED", "BLOCK"] | None = None):
    return request.app.state.database.audit(limit, offset, decision)


@router.get("/audit/{action_id}")
def audit_item(action_id: str, request: Request):
    items = request.app.state.database.audit(identifier=action_id)["items"]
    if not items:
        raise HTTPException(status_code=404, detail="Audit record not found")
    return items[0]
