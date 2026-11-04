import os

from openai import AsyncOpenAI
from dotenv import load_dotenv
from typing import Dict, List

SYSTEM_PROMPT = "请用中文回答用户的问题。"

load_dotenv()


class Myllm:

    def __init__(self, model: str = None, apiKey: str = None, baseUrl: str = None, timeout: int = None):
        self.model = model or os.getenv("LLM_MODEL_ID")
        apiKey = apiKey or os.getenv("LLM_API_KEY")
        baseUrl = baseUrl or os.getenv("LLM_BASE_URL")
        timeout = timeout or int(os.getenv("LLM_TIMEOUT", 60))

        if not all([self.model, apiKey, baseUrl]):
            raise ValueError("模型ID、API密钥和服务地址必须被提供或在.env⽂件中定义")

        self.client = AsyncOpenAI(api_key=apiKey, base_url=baseUrl, timeout=timeout)


    async def think(
        self,
        history: List[Dict[str, str]],
        question: str,
        temperature: float = 0,
    ) -> str:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            *history,
            {"role": "user", "content": question},
        ]
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            stream=True,
        )

        collected_content = []
        async for chunk in response:
            if not chunk.choices:
                continue
            collected_content.append(chunk.choices[0].delta.content or "")
        return "".join(collected_content)
