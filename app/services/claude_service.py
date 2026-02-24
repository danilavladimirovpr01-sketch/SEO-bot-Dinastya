import anthropic
from app.config import ANTHROPIC_API_KEY, MODEL, MAX_TOKENS
from app.prompts.system_prompt import SYSTEM_PROMPT


client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def generate_article(messages: list[dict]) -> str:
    """Send messages to Claude and return the response text."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_PROMPT,
        messages=messages,
    )
    return response.content[0].text


async def generate_article_stream(messages: list[dict]):
    """Stream response from Claude, yielding text chunks."""
    with client.messages.stream(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_PROMPT,
        messages=messages,
    ) as stream:
        for text in stream.text_stream:
            yield text
