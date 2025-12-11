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
    max_tokens: int = 8192,  # 增加 token 限制以支持 V2 详细输出
) -> dict:
    """Send a chat message and parse JSON response."""
    import json
    import re

    system_with_json = system + "\n\nRespond with valid JSON only. No markdown code blocks."

    response = await chat(prompt, system_with_json, max_tokens, temperature=0.3)

    # Clean up response
    response = response.strip()

    # Remove markdown code blocks
    if response.startswith("```"):
        lines = response.split("\n")
        # Find closing ```
        end_idx = len(lines) - 1
        for i in range(len(lines) - 1, 0, -1):
            if lines[i].strip() == "```":
                end_idx = i
                break
        response = "\n".join(lines[1:end_idx])

    # 尝试提取 JSON（处理可能的前后缀文本）
    json_match = re.search(r'\{[\s\S]*\}', response)
    if json_match:
        response = json_match.group()

    try:
        return json.loads(response)
    except json.JSONDecodeError as e:
        # 日志记录失败的响应（截断以避免日志过长）
        from ..utils.logger import get_logger
        logger = get_logger(__name__)
        logger.warning(f"JSON parse error at position {e.pos}: {e.msg}")
        logger.debug(f"Response preview: {response[:500]}...")

        # 返回空结果而非崩溃
        return {}
