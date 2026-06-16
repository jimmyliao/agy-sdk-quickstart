"""Step 2 · streaming — 「回答長就盯著空白等」.

目標：把回覆改成「串流」，字一個個跳出來，不用乾等。
checkpoint：你應該看到文字逐字出現，而不是一次整段跳出。

卡住就：./lab fix 2
"""
import asyncio
import os
import sys

import google.antigravity as ag
import lab_runtime


async def main() -> None:
    cfg = ag.LocalAgentConfig(
        system_instructions="你是繁體中文生活助理，回覆親切口語。",
        model=lab_runtime.model(),
        api_key=os.environ["GEMINI_API_KEY"],
        workspaces=[os.getcwd()],
    )
    async with ag.Agent(cfg) as agent:
        r = await agent.chat("請用三句話介紹『AI agent 跟一般聊天機器人差在哪』。")
        # 直接 async for 迭代 ChatResponse = 串流最終回覆的每個 token
        async for token in r:
            sys.stdout.write(token)
            sys.stdout.flush()
        print()


if __name__ == "__main__":
    lab_runtime.run(main)
