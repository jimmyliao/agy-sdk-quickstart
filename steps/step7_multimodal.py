"""Step 7 · multimodal — 「懶得打字，用說的」（哇點 🍜）.

目標：丟一段語音指令給 agent（原生 Audio 型別），它聽懂後叫外送。
checkpoint：「幫我訂晚餐」.m4a → 🛵 外送成立。
若 assets/order.m4a 不存在 → 自動 fallback 成文字，並提示你補音檔。

卡住就：./lab fix 7
"""
import asyncio
import os

import google.antigravity as ag
import lab_runtime
from google.antigravity import types

from common import order_food

AUDIO = os.path.join(os.path.dirname(__file__), "..", "assets", "order.m4a")


async def main() -> None:
    cfg = ag.LocalAgentConfig(
        system_instructions="你是生活助理，聽懂使用者要吃什麼，用 order_food 叫外送（r01=拉麵 r03=壽司 r04=牛肉麵）。",
        tools=[order_food],
        model=lab_runtime.model(),
        api_key=os.environ["GEMINI_API_KEY"],
        workspaces=[os.getcwd()],
    )
    async with ag.Agent(cfg) as agent:
        if os.path.exists(AUDIO):
            audio = types.Audio.from_file(AUDIO)
            r = await agent.chat(["這是我的語音指令，請照辦：", audio])
        else:
            print("⚠️ 找不到 assets/order.m4a，改用文字示範（要哇點請放一段你預錄的語音）。")
            r = await agent.chat("幫我跟拉麵店點一份豚骨拉麵外送。")
        print("🤖", await r.text())


if __name__ == "__main__":
    lab_runtime.run(main)
