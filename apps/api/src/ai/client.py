"""AI client for Aliyun Bailian (DashScope) API."""

from openai import OpenAI

from ..config import settings

# Lazy initialization
_client: OpenAI | None = None


def get_client() -> OpenAI:
    """Get or create OpenAI-compatible client for DashScope."""
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=settings.dashscope_api_key,
            base_url=settings.dashscope_base_url,
        )
    return _client


async def chat(
    prompt: str,
    system: str = "",
    max_tokens: int = 4096,
    temperature: float = 0.7,
) -> str:
    """Send a chat message to Qwen model."""
    client = get_client()

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model=settings.chat_model,
        max_tokens=max_tokens,
        messages=messages,
        temperature=temperature,
    )

    return response.choices[0].message.content


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
