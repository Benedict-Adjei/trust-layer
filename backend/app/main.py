from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.actions import router as actions_router
from app.api.audit_logs import router as audit_logs_router
from app.api.catalog import router as catalog_router

from app.config import ContextualSettings, load_environment
from app.services.contextual_analyzer import ContextualAnalyzer

from app.database import Database


@asynccontextmanager
async def lifespan(application: FastAPI):
    load_environment()

    application.state.contextual_analyzer = ContextualAnalyzer(
        ContextualSettings.from_environment()
    )

    application.state.database = Database()
    application.state.database.initialize()

    try:
        yield
    finally:
        application.state.database.close()


app = FastAPI(
    title="TrustLayer API",
    description="Security approval and threat detection for AI-agent actions.",
    version="0.1.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(actions_router)
app.include_router(audit_logs_router)
app.include_router(catalog_router)


@app.get("/")
def root():
    return {
        "name": "TrustLayer",
        "message": (
            "Security approval and threat detection "
            "for AI-agent actions."
        ),
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "TrustLayer API",
        "version": "0.1.0",
    }
