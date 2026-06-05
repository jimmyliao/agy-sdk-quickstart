"""Step 6 · middleware / 消費上限 guardrail（optional 緩衝步）— 「給它預算上限」.

目標：用 hook 當守門員，結帳金額 > NT$3000 自動擋下（agent 不知道規則存在）。
checkpoint：超預算時 agent 被攔下，看到「超過上限」訊息。

進度落後可直接跳過，不影響主線。卡住就：./lab fix 6
"""
import asyncio
import os

import google.antigravity as ag
from google.antigravity import types
from google.antigravity.hooks import hooks

from common import add_to_cart, cart_total, checkout, search_products, view_cart

LIMIT = 3000  # 消費上限（新台幣）


@hooks.pre_tool_call_decide
async def budget_guard(data: types.ToolCall) -> types.HookResult:
    if data.name == "checkout":
        total = cart_total()
        if total > LIMIT:
            return types.HookResult(
                allow=False,
                message=f"超過消費上限 NT${LIMIT}（目前 NT${total}），請先移除部分商品。",
            )
    return types.HookResult(allow=True)


async def main() -> None:
    cfg = ag.LocalAgentConfig(
        system_instructions="你是購物助理，使用者要買什麼就查、加購物車、結帳。",
        tools=[search_products, add_to_cart, view_cart, checkout],
        hooks=[budget_guard],
        model="gemini-flash-latest",
        api_key=os.environ["GEMINI_API_KEY"],
        workspaces=[os.getcwd()],
    )
    async with ag.Agent(cfg) as agent:
        r = await agent.chat("幫我買一台 Dyson 吸塵器並結帳。")  # 故意超過 3000
        print("🤖", await r.text())


if __name__ == "__main__":
    asyncio.run(main())
