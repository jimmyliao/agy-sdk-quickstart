"""lab 限流韌性 helper（進階 ./lab 1–8 共用）。

免費金鑰是 per-minute 限流（free tier ~20 次/分），一個 agent 請求會連發好幾次
model call，所以進階步驟很容易撞 429。這支做兩件事：
  · model()    —— 給這個 step 目前可用的模型；撞到會自動換下一個，跨 step 記住
  · run(main)  —— 包住 asyncio.run：撞限流就換 model 重跑這步，真撞頂給友善提示
                  （不是限流的錯照樣 raise，方便 debug）
主玩法 ./lab（play.py）已內建同款防護，這支是給 steps/ 共用，教學 code 維持乾淨。
"""
import asyncio
import logging
import os

MODELS = ["gemini-3.5-flash", "gemini-3.1-flash-lite"]
_STATE = os.path.expanduser("~/.lab_model_idx")

_RL_MARKERS = ("429", "resource_exhausted", "rate limit", "ratelimit", "quota",
               "exhausted", "too many requests", "free_tier")


def _is_rate_limit(s: str) -> bool:
    s = (s or "").lower()
    return any(m in s for m in _RL_MARKERS)


def _idx() -> int:
    try:
        return int(open(_STATE).read().strip())
    except Exception:
        return 0


def _set_idx(i: int) -> None:
    try:
        with open(_STATE, "w") as f:
            f.write(str(i))
    except Exception:
        pass


def model() -> str:
    """目前該用的模型（撞限流後記住換到的那個，跨 step 保留）。"""
    return MODELS[_idx() % len(MODELS)]


class _RLWatch(logging.Handler):
    """攔 SDK 印在 log 的 429（它不一定 raise，有時只印 log）。"""

    def __init__(self):
        super().__init__()
        self.hit = False

    def emit(self, record):
        try:
            if _is_rate_limit(record.getMessage()):
                self.hit = True
        except Exception:
            pass


def _hint() -> None:
    print("\n🐢 撞到免費金鑰的每分鐘上限了（free tier 約 20 次/分，agent 一次會想好幾步）。")
    print("   👉 等約 60 秒再跑一次這步；主玩法 ./lab 不受影響。")


def run(main_func) -> None:
    """包住 asyncio.run(main())：撞限流換 model 重跑這步，真撞頂給提示。
    傳『沒呼叫的』async function（傳 main，不是 main()）。"""
    watch = _RLWatch()
    root = logging.getLogger()
    root.addHandler(watch)
    root.setLevel(logging.WARNING)
    try:
        for attempt in range(len(MODELS)):
            watch.hit = False
            try:
                asyncio.run(main_func())
            except KeyboardInterrupt:
                return
            except Exception as e:  # noqa: BLE001
                if not (_is_rate_limit(str(e)) or watch.hit):
                    raise  # 不是限流 → 真的 bug，照樣噴給你看
                nxt = (_idx() + 1) % len(MODELS)
                _set_idx(nxt)
                if attempt < len(MODELS) - 1:
                    print(f"\n   🔁 撞到限流，換 {MODELS[nxt]} 重跑這步…")
                    continue
                _hint()
                return
            # 沒有例外 = 這步跑完
            if watch.hit:
                print("\n   ⚠️ 剛剛有撞到限流，回答若不完整，等約 60 秒重跑這步。")
            return
        _hint()
    finally:
        root.removeHandler(watch)
