from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="TrustLayer API",
    description="Security approval and threat detection for AI-agent actions.",
    version="0.1.0",
)


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