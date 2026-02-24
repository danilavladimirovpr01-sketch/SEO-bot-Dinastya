from app.config import (
    PROVIDER,
    GEMINI_API_KEY, GEMINI_MODEL,
    ANTHROPIC_API_KEY, ANTHROPIC_MODEL,
    MAX_TOKENS,
)
from app.prompts.system_prompt import SYSTEM_PROMPT


async def generate_article_stream(messages: list[dict]):
    """Stream response from LLM, yielding text chunks. Supports Gemini and Anthropic."""
    if PROVIDER == "gemini":
        async for chunk in _stream_gemini(messages):
            yield chunk
    else:
        async for chunk in _stream_anthropic(messages):
            yield chunk


async def _stream_gemini(messages: list[dict]):
    from google import genai

    client = genai.Client(api_key=GEMINI_API_KEY)

    # Build contents: system instruction is separate, user/assistant messages go into contents
    contents = []
    for msg in messages:
        role = "user" if msg["role"] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": msg["content"]}]})

    response = client.models.generate_content_stream(
        model=GEMINI_MODEL,
        contents=contents,
        config={
            "system_instruction": SYSTEM_PROMPT,
            "max_output_tokens": MAX_TOKENS,
            "temperature": 0.7,
        },
    )

    for chunk in response:
        if chunk.text:
            yield chunk.text


async def _stream_anthropic(messages: list[dict]):
    import anthropic

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    with client.messages.stream(
        model=ANTHROPIC_MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_PROMPT,
        messages=messages,
    ) as stream:
        for text in stream.text_stream:
            yield text
