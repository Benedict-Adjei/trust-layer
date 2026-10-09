"""Compatibility audit endpoints using the same storage as analysis."""
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/audit-logs", tags=["Audit Logs"])


@router.get("")
def get_audit_logs(request: Request, limit: int = Query(50, ge=1, le=200),
                   offset: int = Query(0, ge=0)):
    page = request.app.state.database.audit(limit=limit, offset=offset)
    return {"total": page["total"], "logs": page["items"],
            "limit": limit, "offset": offset}


@router.get("/export")
def export_audit_logs(request: Request):
    page = request.app.state.database.audit(limit=None)
    return JSONResponse(
        content={"export_type": "TrustLayer Audit Log", "total": page["total"],
                 "logs": page["items"]},
        headers={"Content-Disposition": 'attachment; filename="trustlayer_audit_logs.json"'},
    )


@router.get("/{action_id}")
def get_audit_log(action_id: str, request: Request):
    items = request.app.state.database.audit(identifier=action_id)["items"]
    if not items:
        raise HTTPException(status_code=404, detail="Audit log not found")
    return items[0]
