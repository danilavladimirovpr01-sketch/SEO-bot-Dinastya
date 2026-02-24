import requests
from app.config import OPENROUTER_API_KEY, MODEL, MAX_TOKENS
from app.prompts.system_prompt import SYSTEM_PROMPT


def generate_article(messages: list[dict]) -> str:
    """Generate article using Gemini via OpenRouter."""
    full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY.strip()}",
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

    if "error" in data:
        raise Exception(data["error"].get("message", str(data["error"])))

    return data["choices"][0]["message"]["content"]
