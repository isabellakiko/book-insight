"""AI client for Claude API."""

from anthropic import Anthropic

from ..config import settings

# Lazy initialization
_client: Anthropic | None = None


def get_client() -> Anthropic:
    """Get or create Anthropic client."""
    global _client
    if _client is None:
        _client = Anthropic(api_key=settings.anthropic_api_key)
    return _client


async def chat(
    prompt: str,
    system: str = "",
    max_tokens: int = 4096,
    temperature: float = 0.7,
) -> str:
    """Send a chat message to Claude."""
    client = get_client()

    messages = [{"role": "user", "content": prompt}]

    response = client.messages.create(
        model=settings.claude_model,
        max_tokens=max_tokens,
        system=system if system else None,
        messages=messages,
        temperature=temperature,
    )

    return response.content[0].text


async def chat_json(
    prompt: str,
    system: str = "",
    max_tokens: int = 4096,
) -> dict:
    """Send a chat message and parse JSON response."""
    import json

    system_with_json = system + "\n\nRespond with valid JSON only. No markdown code blocks."

    response = await chat(prompt, system_with_json, max_tokens, temperature=0.3)

    # Clean up response
    response = response.strip()
    if response.startswith("```"):
        # Remove markdown code blocks
        lines = response.split("\n")
        response = "\n".join(lines[1:-1])

    return json.loads(response)
