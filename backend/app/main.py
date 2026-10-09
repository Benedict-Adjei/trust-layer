from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
from app.api.actions import router as actions_router
from app.database import Base, engine
from app.models.audit_log import AuditLog
from app.api.audit_logs import router as audit_logs_router


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TrustLayer API",
    description="Security approval and threat detection for AI-agent actions.",
    version="0.1.0",
)
app.include_router(actions_router)
app.include_router(audit_logs_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "name": "TrustLayer",
        "message": "Security approval and threat detection for AI-agent actions."
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "TrustLayer API",
        "version": "0.1.0"
    }