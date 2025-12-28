from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from ..services.caption_engine import generate_caption

router = APIRouter()

class CaptionRequest(BaseModel):
    platform: str = Field(default="instagram")
    tone: str = Field(default="fun")
    imageCount: int = Field(default=1, ge=1, le=20)

    # Optional user input
    userTitle: str = Field(default="")
    userDescription: str = Field(default="")
    context: str = Field(default="")

class CaptionResponse(BaseModel):
    title: str
    description: str
    hashtags: list[str]

@router.post("/generate-caption", response_model=CaptionResponse)
def generate_caption_api(req: CaptionRequest):
    try:
        result = generate_caption(req.model_dump())
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
