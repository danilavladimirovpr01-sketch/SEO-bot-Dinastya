import time
import requests
from app.config import GEMINI_API_KEY, MODEL, MAX_TOKENS
from app.prompts.system_prompt import SYSTEM_PROMPT

MAX_RETRIES = 2
RETRY_DELAY = 5  # seconds


def generate_article(messages: list[dict]) -> str:
    """Generate article using Google Gemini API (OpenAI-compatible endpoint)."""
    full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages

    last_error = None
    for attempt in range(MAX_RETRIES + 1):
        try:
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
                timeout=180,
            )

            data = response.json()

            # Gemini API may return a JSON array instead of object
            if isinstance(data, list):
                data = data[0]

            if "error" in data:
                error_msg = data["error"].get("message", str(data["error"]))
                # Retry on rate limit or server errors
                if response.status_code in (429, 500, 502, 503) and attempt < MAX_RETRIES:
                    last_error = error_msg
                    time.sleep(RETRY_DELAY * (attempt + 1))
                    continue
                raise Exception(error_msg)

            return data["choices"][0]["message"]["content"]

        except requests.exceptions.Timeout:
            last_error = "Превышено время ожидания ответа от API"
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
                continue
        except requests.exceptions.ConnectionError:
            last_error = "Ошибка соединения с API"
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
                continue

    raise Exception(f"{last_error} (после {MAX_RETRIES + 1} попыток)")
