from openai import OpenAI
from .config import OPENAI_API_KEY, OPENAI_MODEL

_client = None

def get_client() -> OpenAI:
    global _client
    if _client is None:
        if not OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY is missing. Set it in your .env file.")
        _client = OpenAI(api_key=OPENAI_API_KEY)
    return _client

# def chat_completion(system_prompt: str, user_prompt: str) -> str:
#     client = get_client()
#     resp = client.chat.completions.create(
#         model=OPENAI_MODEL,
#         temperature=0.8,
#         messages=[
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": user_prompt},
#         ],
#     )
#     return resp.choices[0].message.content or ""
def chat_completion(system_prompt: str, user_prompt: str) -> str:
    client = get_client()
    resp = client.chat.completions.create(
        model=OPENAI_MODEL,
        temperature=0.95,              # more creativity
        presence_penalty=0.7,          # avoid reuse
        frequency_penalty=0.6,         # reduce repetition
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return resp.choices[0].message.content or ""

