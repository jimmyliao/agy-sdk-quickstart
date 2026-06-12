"""Step 5 · hooks — 「它自己亂買怎麼辦？」（高潮點 🎉 結帳賽）.

目標：加一個 pre_tool_call hook，在 checkout 真正送出「前」停下來問你 y/N。
checkpoint：agent 要結帳時跳「確認嗎？[y/N]」→ 按 y → 訂單跳上投影幕 /wall 🎉

卡住就：./lab fix 5
"""
import asyncio
import os

import google.antigravity as ag
from google.antigravity import types
from google.antigravity.hooks import hooks

from common import add_to_cart, cart_total, checkout, clear_cart, search_products, view_cart


@hooks.pre_tool_call_decide
async def approve_checkout(data: types.ToolCall) -> types.HookResult:
    if data.name == "checkout":
        try:
            ans = input(f"\n🚧 agent 想結帳，總額 NT${cart_total()}，確認嗎？[y/N] ")
        except EOFError:
            ans = "y"
        if ans.strip().lower() != "y":
            return types.HookResult(allow=False, message="使用者拒絕結帳")
    return types.HookResult(allow=True)


async def main() -> None:
    cfg = ag.LocalAgentConfig(
        system_instructions="你是購物助理。使用者要買東西時，查商品→加購物車→結帳。"
        "要結帳時【直接呼叫 checkout 工具】，不要先用文字徵求同意——確認由系統關卡處理。",
        tools=[search_products, add_to_cart, view_cart, checkout, clear_cart],
        hooks=[approve_checkout],
        model="gemini-flash-latest",
        api_key=os.environ["GEMINI_API_KEY"],
        workspaces=[os.getcwd()],
    )
    async with ag.Agent(cfg) as agent:
        r = await agent.chat("幫我買一個降噪耳機，然後結帳。")
        print("🤖", await r.text())


if __name__ == "__main__":
    asyncio.run(main())
