# from fastapi import APIRouter, HTTPException
# from pydantic import BaseModel, Field
# from ..services.caption_engine import generate_caption

# router = APIRouter()

# class CaptionRequest(BaseModel):
#     platform: str = Field(default="instagram")
#     tone: str = Field(default="fun")
#     imageCount: int = Field(default=1, ge=1, le=20)

#     # Optional user input
#     userTitle: str = Field(default="")
#     userDescription: str = Field(default="")
#     context: str = Field(default="")

# class CaptionResponse(BaseModel):
#     title: str
#     description: str
#     hashtags: list[str]

# @router.post("/generate-caption", response_model=CaptionResponse)
# def generate_caption_api(req: CaptionRequest):
#     try:
#         result = generate_caption(req.model_dump())
#         return result
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))
import json
import random
from pathlib import Path
from typing import Dict, Any

from fastapi import APIRouter

from ..core.openai_client import chat_completion

router = APIRouter()


# 🔹 Prompt path (v2)
PROMPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "prompts"
    / "v2_travel.txt"
)


@router.post("/generate-caption")
def generate(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    API endpoint to generate title, description, and hashtags.
    """
    return generate_caption(payload)


def _load_system_prompt() -> str:
    """
    Load system prompt (v2) from prompts directory.
    """
    if not PROMPT_PATH.exists():
        raise FileNotFoundError("System prompt file not found.")
    return PROMPT_PATH.read_text(encoding="utf-8")


def _safe_json(text: str) -> Dict[str, Any]:
    """
    Safely parse JSON returned by the model.
    Attempts extraction if extra text exists.
    """
    text = text.strip()

    # 1️⃣ Direct parse
    try:
        return json.loads(text)
    except Exception:
        pass

    # 2️⃣ Extract JSON block
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except Exception:
            pass

    raise ValueError("Model did not return valid JSON.")


def generate_caption(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main caption generation engine.
    Handles creativity, variation, and normalization.
    """

    system_prompt = _load_system_prompt()

    # 🔹 Input extraction
    platform = payload.get("platform", "instagram")
    tone = payload.get("tone", "fun")
    user_title = payload.get("userTitle", "")
    user_desc = payload.get("userDescription", "")
    extra_context = payload.get("context", "")
    image_count = int(payload.get("imageCount", 1))

    # 🔹 Creative variation
    creative_angles = [
        "focus on atmosphere and mood",
        "focus on movement and action",
        "focus on quiet personal moments",
        "focus on visual contrast and light",
        "focus on reflection and meaning",
    ]
    creative_angle = random.choice(creative_angles)

    # 🔹 User prompt
    user_prompt = f"""
Platform: {platform}
Tone: {tone}
ImageCount: {image_count}

Creative Angle: {creative_angle}

User Provided Title: {user_title}
User Provided Description: {user_desc}
Extra Context: {extra_context}

Task:
- If user text exists, refine without changing meaning.
- If missing, generate fresh, non-generic captions.
- Follow platform, tone, and creative angle strictly.
- Never reuse phrasing from common travel captions.
- Return ONLY valid JSON.
""".strip()

    # 🔹 OpenAI call
    raw_response = chat_completion(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )

    data = _safe_json(raw_response)

    # 🔹 Normalize output
    title = str(data.get("title", "")).strip()[:80]
    description = str(data.get("description", "")).strip()[:500]
    hashtags = data.get("hashtags", [])

    if not isinstance(hashtags, list):
        hashtags = []

    hashtags = [
        tag.strip()
        for tag in hashtags
        if isinstance(tag, str) and tag.strip().startswith("#")
    ]

    return {
        "title": title,
        "description": description,
        "hashtags": hashtags,
    }
