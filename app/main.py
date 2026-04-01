import os
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {
        "message": "DevOps Lab v3 - GitOps with ArgoCD!",
        "env": os.getenv("APP_ENV", "not set"),
        "version": os.getenv("APP_VERSION", "not set"),
        "log_level": os.getenv("LOG_LEVEL", "not set")
    }

@app.get("/secret-check")
def secret_check():
    api_key = os.getenv("API_KEY", "not set")
    return {
        "api_key_exists": api_key != "not set",
        "api_key_length": len(api_key)
    }
