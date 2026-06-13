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
    "你是親切俐落的購物與生活助理。使用者要找東西用 search_products、加購物車用 add_to_cart、"
    "看購物車用 view_cart、結帳用 checkout、叫外送用 order_food、訂位用 book_table。"
    "使用者說『買/結帳/下單』時，把該加的加進購物車後【直接呼叫 checkout 工具完成結帳】，"
    "不要只用文字問要不要，直接做。回答簡短、繁體中文。"
)

INTRO = """🛒 歡迎來到 AgentMall！我是你的購物 agent。

想買什麼、想吃什麼、想訂位？直接打字跟我說就好，例如：
   · 幫我找一個降噪耳機，然後結帳
   · 我想叫一份拉麵外送
   · 幫我訂今晚 7 點 2 個人的位子
   · 預算 500 內推薦點咖啡

（打字後你會看到三層鏈：🔧 我決定用哪個工具 → 🌐 真的打商城 → 🤖 我回你。
  結帳成功，你的訂單會即時跳上投影幕 /wall 🎉   輸入 exit 離開。）"""


async def main():
    if not os.environ.get("GEMINI_API_KEY"):
        print("⚠️ 還沒設 GEMINI_API_KEY —— 先貼上 signup 給你的兩行 export 再跑 ./lab")
        sys.exit(1)
    student = os.environ.get("STUDENT_ID", "guest")
    print(INTRO)
    print(f"\n（你的身分：{student} · 訂單會以這個名字上牆）")

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
            try:
                r = await agent.chat(msg)
                txt = await r.text()
            except Exception as e:
                txt = str(e)
            if _is_rate_limit(txt):
                _rate_limit_hint()
            elif txt.strip():
                print(f"🤖 {txt}")
            else:
                print("⚠️ 這次沒拿到回應，再試一次；或 ./lab check 看看環境。")


# 免費金鑰每分鐘有呼叫上限（~10-15 RPM）；連續快速玩會撞到 → 給友善提示而非生 error
_RL_MARKERS = ("429", "resource_exhausted", "rate limit", "ratelimit", "quota", "exhausted", "too many requests")


def _is_rate_limit(s: str) -> bool:
    s = (s or "").lower()
    return any(m in s for m in _RL_MARKERS)


def _rate_limit_hint() -> None:
    print("🐢 慢一點～你的免費金鑰每分鐘有呼叫上限（約 10–15 次）。")
    print("   一個請求 agent 會想好幾步，所以連續快玩很容易到頂。")
    print("   👉 等 30–60 秒再試，或一步一步慢慢來，通常就不會撞到。")


if __name__ == "__main__":
    asyncio.run(main())
