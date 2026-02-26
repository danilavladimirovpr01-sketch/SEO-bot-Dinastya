import requests
from app.config import GEMINI_API_KEY, MODEL, MAX_TOKENS
from app.prompts.system_prompt import SYSTEM_PROMPT


def generate_article(messages: list[dict]) -> str:
    """Generate article using Google Gemini API (OpenAI-compatible endpoint)."""
    full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages

    response = requests.post(
        "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
        headers={
            "Authorization": f"Bearer {GEMINI_API_KEY.strip()}",
            "Content-Type": "application/json",
        },
        json={
            "model": MODEL,
            "messages": full_messages,
            "max_tokens": MAX_TOKENS,
            "temperature": 0.7,
        },
        timeout=120,
    )

    data = response.json()

    # Gemini API may return a JSON array instead of object
    if isinstance(data, list):
        data = data[0]

    if "error" in data:
        raise Exception(data["error"].get("message", str(data["error"])))

    return data["choices"][0]["message"]["content"]
