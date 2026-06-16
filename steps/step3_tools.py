"""Step 3 · tools — 「它不知道商店有什麼、今天天氣」（魔法時刻 ✨）.

目標：掛上兩個 tool（search_products + get_weather），
讓 agent 真的去查 shop.leapcore.tw。
checkpoint：問「有耳機嗎？」→ agent 真的查到 🎧 並報出價格。

卡住就：./lab fix 3
"""
import asyncio
import os

import google.antigravity as ag
import lab_runtime

from common import get_weather, search_products


async def main() -> None:
    cfg = ag.LocalAgentConfig(
        system_instructions="你是繁體中文購物助理。需要商品或天氣資訊時，務必呼叫工具查證，不要自己編。",
        tools=[search_products, get_weather],
        model=lab_runtime.model(),
        api_key=os.environ["GEMINI_API_KEY"],
        workspaces=[os.getcwd()],
    )
    async with ag.Agent(cfg) as agent:
        r = await agent.chat("店裡有降噪耳機嗎？順便告訴我台北今天天氣。")
        print("🤖", await r.text())


if __name__ == "__main__":
    lab_runtime.run(main)
