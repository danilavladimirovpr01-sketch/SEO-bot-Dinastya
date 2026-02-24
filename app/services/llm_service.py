from google import genai
from app.config import GEMINI_API_KEY, GEMINI_MODEL, MAX_TOKENS
from app.prompts.system_prompt import SYSTEM_PROMPT


def generate_article(messages: list[dict]) -> str:
    """Generate article using Google Gemini."""
    client = genai.Client(api_key=GEMINI_API_KEY)

    contents = []
    for msg in messages:
        role = "user" if msg["role"] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": msg["content"]}]})

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=contents,
        config={
            "system_instruction": SYSTEM_PROMPT,
            "max_output_tokens": MAX_TOKENS,
            "temperature": 0.7,
        },
    )

    return response.text
