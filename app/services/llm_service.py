from app.config import (
    PROVIDER,
    GEMINI_API_KEY, GEMINI_MODEL,
    ANTHROPIC_API_KEY, ANTHROPIC_MODEL,
    MAX_TOKENS,
)
from app.prompts.system_prompt import SYSTEM_PROMPT


def generate_article(messages: list[dict]) -> str:
    """Generate full response from LLM. Supports Gemini and Anthropic."""
    if PROVIDER == "gemini":
        return _generate_gemini(messages)
    else:
        return _generate_anthropic(messages)


def _generate_gemini(messages: list[dict]) -> str:
    from google import genai

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


def _generate_anthropic(messages: list[dict]) -> str:
    import anthropic

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    response = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_PROMPT,
        messages=messages,
    )

    return response.content[0].text
