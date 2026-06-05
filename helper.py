"""🤖 小助教 agent — 用 agent 學 agent.

卡住時開第二個分頁跑：uv run python helper.py
它會載入「官方 Antigravity SDK skill」當知識庫，回答你關於 SDK 的問題。

機制：
  1. 把官方 SDK repo 的 skills/google-antigravity-sdk/ 拷進本 repo 的
     vendor/google-antigravity-sdk/（第一次會 git clone --depth 1 到 ~/.cache）。
  2. 用 LocalAgentConfig(skills_paths=[...]) 把 skill 餵給 agent。
  3. clone 失敗就退化成「一般 SDK 問答」agent（仍可用，只是沒有官方 skill 加持）。
"""
import asyncio
import os
import shutil
import subprocess
import sys
import tempfile

import google.antigravity as ag

REPO = os.path.dirname(os.path.abspath(__file__))
VENDOR = os.path.join(REPO, "vendor", "google-antigravity-sdk")
SDK_GIT = "https://github.com/google-antigravity/antigravity-sdk-python"
CACHE = os.path.join(os.path.expanduser("~"), ".cache", "agy-skill")


def ensure_skill() -> str | None:
    """確保 vendor/google-antigravity-sdk 存在，回傳路徑；失敗回 None。"""
    if os.path.exists(os.path.join(VENDOR, "SKILL.md")):
        return VENDOR
    src_skill = os.path.join(CACHE, "skills", "google-antigravity-sdk")
    if not os.path.exists(src_skill):
        try:
            if os.path.exists(CACHE):
                shutil.rmtree(CACHE)
            print("📥 第一次啟動：拉官方 SDK skill（git clone --depth 1）…")
            subprocess.run(
                ["git", "clone", "--depth", "1", SDK_GIT, CACHE],
                check=True, capture_output=True, timeout=120,
            )
        except Exception as e:
            print(f"⚠️ clone 失敗（{e}）→ 改用一般 SDK 問答模式。")
            return None
    try:
        os.makedirs(os.path.dirname(VENDOR), exist_ok=True)
        shutil.copytree(src_skill, VENDOR, dirs_exist_ok=True)
        return VENDOR
    except Exception as e:
        print(f"⚠️ 拷貝 skill 失敗（{e}）→ 改用一般 SDK 問答模式。")
        return None


async def main() -> None:
    if not os.environ.get("GEMINI_API_KEY"):
        print("❌ 先設 GEMINI_API_KEY（照 signup 卡片 export）再開小助教。")
        sys.exit(1)

    skill = ensure_skill()
    sys_inst = (
        "你是 Antigravity SDK 小助教，用繁體中文、簡短可執行地回答學員問題，"
        "盡量附上一小段 code 範例。"
    )
    kwargs = dict(
        system_instructions=sys_inst,
        model="gemini-flash-latest",
        api_key=os.environ["GEMINI_API_KEY"],
        workspaces=[REPO],
    )
    if skill:
        kwargs["skills_paths"] = [skill]
        print(f"✅ 已載入官方 SDK skill：{skill}")
    else:
        print("ℹ️ 無 skill，仍可問一般 SDK 問題。")

    cfg = ag.LocalAgentConfig(**kwargs)
    print("🤖 小助教上線！輸入問題，或 exit 離開。\n")
    async with ag.Agent(cfg) as agent:
        while True:
            try:
                q = input("你 > ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n掰掰 👋")
                break
            if not q:
                continue
            if q.lower() in ("exit", "quit", "q"):
                print("掰掰 👋")
                break
            r = await agent.chat(q)
            print("🤖", await r.text(), "\n")


if __name__ == "__main__":
    asyncio.run(main())
