
from functools import lru_cache

from langchain_openai import ChatOpenAI

from app.core.config import (
    LLM_API_KEY,
    LLM_BASE_URL,
    LLM_MODEL_NAME,
    LLM_TEMPERATURE,
    LLM_TIMEOUT,
)


@lru_cache(maxsize=1)
def get_llm() -> ChatOpenAI:
    if not LLM_API_KEY:
        raise RuntimeError("缺少 LLM_API_KEY，请先在 fund_agent/.env 中配置。")
    if not LLM_MODEL_NAME:
        raise RuntimeError("缺少 LLM_MODEL_NAME，请先在 fund_agent/.env 中配置。")

    return ChatOpenAI(
        model=LLM_MODEL_NAME,
        api_key=LLM_API_KEY,
        base_url=LLM_BASE_URL,
        temperature=LLM_TEMPERATURE,
        timeout=LLM_TIMEOUT,
    )


# 