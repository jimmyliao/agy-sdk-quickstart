"""Step 8 · doc agent — 「幫我記帳」（E2E 完成 🏁）.

目標：讓 agent 自己「寫檔案」——查你今晚的訂單，產出 my-life-report.md。
checkpoint：跑完 ls 看到 my-life-report.md，打開是完整消費報告。

agent 用內建的 create_file 工具寫檔（workspaces 圈住目前資料夾才有權限）。
卡住就：./lab fix 8
"""
import asyncio
import os

import google.antigravity as ag

from common import STUDENT, view_cart


def my_orders() -> dict:
    """查我（目前學員）今晚在商城的購物車與訂單摘要，給報告用。"""
    return {"student": STUDENT, "cart": view_cart()}


async def main() -> None:
    cfg = ag.LocalAgentConfig(
        system_instructions=(
            "你是記帳助理。請呼叫 my_orders 取得我的消費資料，"
            "然後用 create_file 在工作目錄寫一份 my-life-report.md，"
            "內容含：標題、今晚消費總結、明細表、一句溫馨結語，全部繁體中文。"
        ),
        tools=[my_orders],
        model="gemini-flash-latest",
        api_key=os.environ["GEMINI_API_KEY"],
        workspaces=[os.getcwd()],  # 給 agent 在此資料夾寫檔的權限
    )
    async with ag.Agent(cfg) as agent:
        r = await agent.chat("幫我把今晚的消費整理成 my-life-report.md。")
        print("🤖", await r.text())
        print("\n✅ 打開 my-life-report.md 看看你的消費報告！")


if __name__ == "__main__":
    asyncio.run(main())
