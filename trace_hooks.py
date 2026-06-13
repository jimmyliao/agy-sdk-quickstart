"""🔧 學習模式 hooks — 讓小白「看得見」agy SDK 在編排 agent。

把 TRACE_HOOKS 加進你的 agent：

    from trace_hooks import TRACE_HOOKS
    cfg = ag.LocalAgentConfig(..., hooks=TRACE_HOOKS)

跑起來你會看到三層鏈：
    🔧 agent 決定用工具：search_products(q='降噪耳機')   ← agy SDK 在編排
       🌐 GET /products → ✅ 200 · 1 件 · 76ms          ← 真的打商城（common.py 印的）
    🤖 找到 Sony WH-1000XM5...                          ← agent 回答

設 LAB_TRACE=0 可整個關掉。
"""
import os

from google.antigravity import types
from google.antigravity.hooks import hooks

_TRACE = os.environ.get("LAB_TRACE", "1") != "0"


@hooks.pre_tool_call_decide
async def _trace_tool(data: types.ToolCall) -> types.HookResult:
    """agent 每次要呼叫工具前，先印出來（不擋，純觀察）。"""
    if _TRACE:
        args = data.args or {}
        argstr = ", ".join(f"{k}={v!r}" for k, v in args.items())
        print(f"🔧 agent 決定用工具：{data.name}({argstr})")
    return types.HookResult(allow=True)


@hooks.on_tool_error
async def _trace_error(data) -> None:
    """工具出錯時，給一句友善說明（小白才不會被 traceback 嚇到）。"""
    if _TRACE:
        name = getattr(data, "name", "工具")
        print(f"   ⚠️ {name} 執行出錯了 —— 看上面 🌐 的 ❌ 行找原因；卡住就 ./lab fix N 或舉手。")


# 學員直接 import 這個，貼進 hooks=[...]
TRACE_HOOKS = [_trace_tool, _trace_error]
