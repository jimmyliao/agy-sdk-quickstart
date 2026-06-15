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
import logging
import os
import sys

import google.antigravity as ag

from common import (add_to_cart, book_table, checkout, clear_cart, get_weather,
                    order_food, search_products, view_cart)
from trace_hooks import TRACE_HOOKS

TOOLS = [search_products, get_weather, add_to_cart, view_cart, clear_cart,
         checkout, order_food, book_table]

# model fallback：免費層每個 model 有獨立 RPM（~5/分鐘），撞了就換下一個 → 額度疊加
MODELS = ["gemini-3.5-flash", "gemini-3.1-flash-lite"]

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


# ── rate-limit 偵測 ──────────────────────────────────
# 免費金鑰 RPM 很低（gemini-flash 免費層 5 次/分鐘）；撞到時 SDK 把 429 印在 log，
# 且會「關掉 agent session（WebSocket 1000）」→ 之後回 garbage。所以要：
#   ① 從 log 抓 429  ② 偵測 1000 garbage  ③ 每輪用全新 agent 避免 session 中毒
_RL_MARKERS = ("429", "resource_exhausted", "rate limit", "ratelimit", "quota",
               "exhausted", "too many requests", "free_tier")


def _is_rate_limit(s: str) -> bool:
    s = (s or "").lower()
    return any(m in s for m in _RL_MARKERS)


def _looks_broken(s: str) -> bool:
    # 429 殺掉 session 後，後續 chat 會回 WebSocket 關閉碼之類的 garbage
    s = (s or "").lower()
    return ("received 1000" in s) or ("sent 1000" in s) or (s.strip() == "ok")


def _rate_limit_hint() -> None:
    print("🐢 撞到免費金鑰的每分鐘上限了（gemini-flash 免費層只有 5 次/分鐘）。")
    print("   一個請求 agent 會想好幾步，所以一兩個動作就到頂。")
    print("   👉 等約 60 秒再打字就能繼續（agent 已自動重開，不會卡死）。")


class _RLWatch(logging.Handler):
    """攔 SDK 印在 log 的 429（不在回傳/例外裡，要從 log 抓）。"""
    def __init__(self):
        super().__init__()
        self.hit = False

    def emit(self, record):
        try:
            if _is_rate_limit(record.getMessage()):
                self.hit = True
        except Exception:
            pass


_rl_watch = _RLWatch()
logging.getLogger().addHandler(_rl_watch)
logging.getLogger().setLevel(logging.WARNING)


async def main():
    if not os.environ.get("GEMINI_API_KEY"):
        print("⚠️ 還沒設 GEMINI_API_KEY —— 到 ai.dev/apikey 拿免費金鑰，export 後再跑 ./lab")
        sys.exit(1)
    student = os.environ.get("STUDENT_ID", "guest")
    api_key = os.environ["GEMINI_API_KEY"]
    print(INTRO)
    print(f"\n（你的身分：{student} · 訂單會以這個名字上牆）")

    def make_cfg(model):
        return ag.LocalAgentConfig(
            system_instructions=SYSTEM, tools=TOOLS, hooks=TRACE_HOOKS,
            model=model, api_key=api_key, workspaces=[os.getcwd()],
        )

    model_idx = 0  # 記住目前可用的 model，跨輪保留 → 不用每輪都先撞一次 3.5-flash
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
        txt, ok = "", False
        # 從「上次可用的 model」開始試；撞 RPM 才換下一個（每輪全新 agent，避免 session 中毒）
        for _ in range(len(MODELS)):
            model = MODELS[model_idx]
            _rl_watch.hit = False
            try:
                async with ag.Agent(make_cfg(model)) as agent:
                    r = await agent.chat(msg)
                    txt = await r.text()
            except Exception as e:
                txt = str(e)
            if not (_rl_watch.hit or _is_rate_limit(txt) or _looks_broken(txt)):
                ok = True
                break
            nxt = (model_idx + 1) % len(MODELS)
            print(f"   🔁 {model} 額度滿了，換 {MODELS[nxt]} 繼續…")
            model_idx = nxt  # 記住換到的 model，下一輪直接從這開始
        if ok and txt.strip():
            print(f"🤖 {txt}")
        elif not ok:
            _rate_limit_hint()
        else:
            print("⚠️ 這次沒拿到完整回應，等一下再試一次；或 ./lab check 看看環境。")


if __name__ == "__main__":
    asyncio.run(main())
