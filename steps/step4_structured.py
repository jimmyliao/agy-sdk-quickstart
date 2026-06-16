"""Step 4 · structured output — 「我要的是清單不是散文」.

目標：定一個 JSON schema（購物建議），讓 agent 回「結構化資料」而非一段話。
checkpoint：你應該看到整齊的 JSON，每筆有 品名/價格/推薦理由。

卡住就：./lab fix 4
"""
import asyncio
import json
import os

import google.antigravity as ag
import lab_runtime
import pydantic

from common import search_products


class Pick(pydantic.BaseModel):
    name: str        # 品名
    price: int       # 價格（新台幣）
    reason: str      # 推薦理由（繁體中文）


class Advice(pydantic.BaseModel):
    picks: list[Pick]


async def main() -> None:
    cfg = ag.LocalAgentConfig(
        system_instructions="你是購物顧問，先用工具查商品，再依預算給結構化建議。",
        tools=[search_products],
        response_schema=Advice,          # 關鍵：指定回傳 schema
        model=lab_runtime.model(),
        api_key=os.environ["GEMINI_API_KEY"],
        workspaces=[os.getcwd()],
    )
    async with ag.Agent(cfg) as agent:
        r = await agent.chat("預算 3000 元內，推薦我三樣 3C 好物，給理由。")
        data = await r.structured_output()      # 回傳 dict
        print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    lab_runtime.run(main)
