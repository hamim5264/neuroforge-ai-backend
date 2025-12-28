from fastapi import FastAPI
from .api.caption import router as caption_router

app = FastAPI(title="NeuroForge AI", version="1.0.0")

app.include_router(caption_router, prefix="/api")

@app.get("/health")
def health():
    return {"status": "ok"}
