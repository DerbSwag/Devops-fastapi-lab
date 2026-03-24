from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "DevOps Lab v2 - CD Pipeline Works!"}
