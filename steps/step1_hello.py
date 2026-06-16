"""Step 1 · hello world — 「我想要一個生活助理」.

目標：用最少的 code 把 agent 叫起來，請它用中文自我介紹。
checkpoint：你應該看到 agent 用「中文」自我介紹（不是英文）。

卡住就：./lab fix 1
"""
import asyncio
import os

import google.antigravity as ag
import lab_runtime


async def main() -> None:
    cfg = ag.LocalAgentConfig(
        system_instructions="你是一個友善的繁體中文生活助理，所有回覆都用繁體中文。",
        model=lab_runtime.model(),
        api_key=os.environ["GEMINI_API_KEY"],
        workspaces=[os.getcwd()],
    )
    async with ag.Agent(cfg) as agent:
        r = await agent.chat("用一句話跟我自我介紹，你能幫我做什麼？")
        print("🤖", await r.text())  # .text() 才會真的去打模型


if __name__ == "__main__":
    lab_runtime.run(main)
