import json
from pathlib import Path
from ..core.openai_client import chat_completion

PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "v1_travel.txt"

def _load_system_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")

def _safe_json(text: str) -> dict:
    """
    Tries to parse JSON. If the model wrapped JSON with text, attempt extraction.
    """
    text = text.strip()

    # First attempt
    try:
        return json.loads(text)
    except Exception:
        pass

    # Try to extract JSON object substring
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start : end + 1])
        except Exception:
            pass

    raise ValueError("Model did not return valid JSON.")

def generate_caption(payload: dict) -> dict:
    system_prompt = _load_system_prompt()

    platform = payload.get("platform", "instagram")
    tone = payload.get("tone", "fun")
    user_title = payload.get("userTitle", "")
    user_desc = payload.get("userDescription", "")
    extra_context = payload.get("context", "")
    image_count = int(payload.get("imageCount", 1))

    user_prompt = f"""
Platform: {platform}
Tone: {tone}
ImageCount: {image_count}

User Provided Title: {user_title}
User Provided Description: {user_desc}
Extra Context (optional): {extra_context}

Task:
- If user provided a title/description, improve them while keeping the meaning.
- If missing, generate the best fitting title/description for travel/nature photos.
Return JSON exactly in the schema.
""".strip()

    raw = chat_completion(system_prompt=system_prompt, user_prompt=user_prompt)
    data = _safe_json(raw)

    # Basic normalization
    title = str(data.get("title", "")).strip()[:80]
    description = str(data.get("description", "")).strip()[:500]
    hashtags = data.get("hashtags", [])
    if not isinstance(hashtags, list):
        hashtags = []

    hashtags = [str(h).strip() for h in hashtags if str(h).strip().startswith("#")]

    return {"title": title, "description": description, "hashtags": hashtags}
