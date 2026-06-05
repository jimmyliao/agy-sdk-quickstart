# agy-sdk-quickstart 🚀

**Build with AI 2026 Taipei — Antigravity SDK 實戰：在 Cloud Shell 上建出你的第一個 AI Agent**
6/16 (Tue) 19:00–21:30 · CAAM 承德168

> 🚧 Workshop 教材建置中，**活動當天由 private 轉為 public**。
> （sibling repo: [agy-cli-quickstart](https://github.com/jimmyliao/agy-cli-quickstart) — CLI 版 lab @ BWAI Tainan 2026-05-23）

一個晚上，你會把一隻「生活助理 agent」一步步建出來：它會查商品、問天氣、放購物車、
**結帳前停下來問你**、叫外送、訂位，最後自動產出一份消費報告檔案。
大家的 agent 都連到同一個 mock 世界 `shop.leapcore.tw`，**訂單即時跳上投影幕 /wall** 🎉

## 🏁 三步開始

```bash
./setup.sh                       # 1. 環境暖機（uv / 依賴 / 連線）
export GEMINI_API_KEY=AIza...    # 2. 貼上 signup 卡片的兩行
export STUDENT_ID=你的暱稱
./lab check                      # 3. 體檢，全 ✅ 就開跑
./lab 1                          #    第一步！
```

> Cloud Shell 學員：點商城上的 **Open in Cloud Shell** 會自動 clone 本 repo 並展開
> `tutorial.md` 側欄，照著貼指令即可。

## 🧰 `./lab` 一個字搞定

| 指令 | 作用 |
|---|---|
| `./lab N` | 跑 step N（1–8） |
| `./lab fix N` | 卡住？把 `solutions/stepN` 拷回 `steps/` |
| `./lab check` | 環境體檢（key / 商城 / SDK 各印 ✅/❌） |

🤖 還是卡住？開**第二個分頁**問小助教：`uv run python helper.py`（用 agent 學 agent）。

## 🪜 八步在做什麼

| # | 步驟 | 學到的 SDK 能力 |
|---|---|---|
| 1 | hello world | 建 Agent、中文自介 |
| 2 | streaming | `async for token in response` 逐字串流 |
| 3 | tools | 掛普通函式當 agent 的手（查商品＋天氣）✨ |
| 4 | structured output | `response_schema` → 拿到 JSON |
| 5 | hooks | `pre_tool_call_decide` 結帳前人工核可 🎉 |
| 6 | guardrail | hook 做消費上限（optional） |
| 7 | multimodal | 丟語音 `types.Audio` → 點外送 🍜 |
| 8 | doc agent | agent 用內建 `create_file` 自動寫報告 🏁 |

## 📁 結構

```
setup.sh        # 環境一鍵就緒（uv / 依賴暖機 / shop 連線檢查）
lab             # ./lab N 跑步 · ./lab fix N 拷解答 · ./lab check 體檢
tutorial.md     # Cloud Shell 教學側欄
common.py       # AgentMall (shop.leapcore.tw) tools — agent 的「手」
helper.py       # 🤖 小助教 agent（載入官方 SDK skill）
steps/          # step1..8（每檔 ≤35 行，頂部 docstring = 目標+checkpoint）
solutions/      # 完整解答
```

## 📚 官方資源

- SDK: <https://github.com/google-antigravity/antigravity-sdk-python>
- Examples: `examples/getting_started`（單功能）＋ `examples/deep_dives`（進階）
- Skills: `skills/google-antigravity-sdk/`（13 篇給 AI 看的教學 md）

---

執行環境：Python ≥ 3.11，一律用 [`uv`](https://docs.astral.sh/uv/)。
