"""🎮 ./lab play — 先玩再學：零編輯，直接跟你的購物 agent 說話.

第一次體驗 agy SDK 最快的方式：不用改任何 code，打字就好。
你會看到「三層鏈」：
    🔧 agent 決定用哪個工具   ← agy SDK 在編排
    🌐 真的打商城 shop.leapcore.tw（status/耗時/錯誤）
    🤖 agent 回你話
結帳成功 → 你的訂單即時跳上投影幕 /wall 🎉

試試看打：
    幫我找一個降噪耳機，加進購物車
    我的購物車有什麼？
    幫我結帳
輸入 exit 離開。
"""
import asyncio
import os
import sys

import google.antigravity as ag

from common import (add_to_cart, book_table, checkout, clear_cart, get_weather,
                    order_food, search_products, view_cart)
from trace_hooks import TRACE_HOOKS

TOOLS = [search_products, get_weather, add_to_cart, view_cart, clear_cart,
         checkout, order_food, book_table]

SYSTEM = (
    "你是親切的購物與生活助理。使用者要找東西用 search_products、加購物車用 add_to_cart、"
    "看購物車用 view_cart、結帳用 checkout、叫外送用 order_food、訂位用 book_table。"
    "要結帳時直接呼叫 checkout 工具。回答簡短、繁體中文。"
)


async def main():
    if not os.environ.get("GEMINI_API_KEY"):
        print("⚠️ 還沒設 GEMINI_API_KEY —— 先貼上 signup 給你的兩行 export 再跑 ./lab play")
        sys.exit(1)
    student = os.environ.get("STUDENT_ID", "guest")
    print(__doc__)
    print(f"（你的身分：{student} · 訂單會以這個名字上牆）\n")

    cfg = ag.LocalAgentConfig(
        system_instructions=SYSTEM,
        tools=TOOLS,
        hooks=TRACE_HOOKS,
        model="gemini-flash-latest",
        api_key=os.environ["GEMINI_API_KEY"],
        workspaces=[os.getcwd()],
    )
    async with ag.Agent(cfg) as agent:
        while True:
            try:
                msg = input("\n你 > ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n掰掰，接著去跑 ./lab 1 學怎麼自己建出這隻 agent！")
                return
            if not msg:
                continue
            if msg.lower() in ("exit", "quit", "bye", "掰掰"):
                print("掰掰，接著去跑 ./lab 1 學怎麼自己建出這隻 agent！")
                return
            print()  # 讓三層鏈跟你的輸入隔開
            r = await agent.chat(msg)
            print(f"🤖 {await r.text()}")


if __name__ == "__main__":
    asyncio.run(main())
