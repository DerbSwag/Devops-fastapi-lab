import os
from fastapi import FastAPI, Response

app = FastAPI()

# Track readiness state — can be extended to check DB, cache, etc.
_ready = True


@app.get("/")
def read_root():
    return {
        "message": "DevOps Lab v3 - GitOps with ArgoCD!",
        "env": os.getenv("APP_ENV", "not set"),
        "version": os.getenv("APP_VERSION", "not set"),
        "log_level": os.getenv("LOG_LEVEL", "not set"),
    }


@app.get("/healthz")
def liveness():
    """Liveness probe — if this fails, K8s will restart the pod."""
    return {"status": "alive"}


@app.get("/readyz")
def readiness(response: Response):
    """Readiness probe — if this fails, K8s removes the pod from Service endpoints."""
    if not _ready:
        response.status_code = 503
        return {"status": "not ready"}
    return {"status": "ready"}


@app.get("/secret-check")
def secret_check():
    api_key = os.getenv("API_KEY", "not set")
    return {
        "api_key_exists": api_key != "not set",
        "api_key_length": len(api_key),
    }
