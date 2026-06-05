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
| `./lab N` | 跑 step N（1–8，外加選做 9） |
| `./lab fix N` | 卡住？把 `solutions/stepN` 拷回 `steps/` |
| `./lab check` | 環境體檢（key / 商城 / SDK 各印 ✅/❌） |
| `./lab 9` | 🎤 選做：啟動「跟你的 agent 說話」語音網頁（Cloud Shell 網頁預覽 8080） |

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
| 9 | voice web（選做）| 開網頁、**按住麥克風講話**跟 agent 對話 🎤（FastAPI/uvicorn + 瀏覽器麥克風）|

## 🎤 Step 9（選做）：跟你的 agent 說話

時間有餘的話玩這關。它把前面那隻 agent 包進一個**手機友善的網頁**，
你直接「按住 🎤 講話」就能下指令。

```bash
./lab 9          # 啟動語音網頁（uvicorn 0.0.0.0:8080）
```

**在 Cloud Shell 看畫面**：右上角點 **「網頁預覽」**（一個小螢幕 icon）→
**「透過以下連接埠預覽」→ 8080**，瀏覽器就會開出錄音頁。

頁面有三條輸入路徑（由易到難保底）：
1. **主模式**：按住 🎤 錄音 → 放開送出（走原生 `types.Audio` 多模態）。
2. **🗣️ 瀏覽器轉文字**：Chrome 內建 Web Speech API，辨識成文字再送。
3. **純文字輸入框**：最終保底，打字也能用。

> ⚠️ **webm 相容性**：瀏覽器 `MediaRecorder` 多半錄成 `webm/opus`，但 SDK 的
> `types.Audio` 只收 wav/mp3/ogg/aac/flac/m4a。後端會在有 `ffmpeg` 時自動把
> webm 轉成 ogg/opus；**沒有 ffmpeg 又錄到 webm 時，請改用「🗣️ 轉文字」按鈕**。
> Cloud Shell 通常有 ffmpeg，本機若沒有就靠轉文字保底。

> ⚠️ 這關的結帳走「**web 模式自動核可**」（網頁沒有終端機可以按 y/N），
> agent 想結帳會直接成立，試玩時請留意。

## 📁 結構

```
setup.sh        # 環境一鍵就緒（uv / 依賴暖機 / shop 連線檢查）
lab             # ./lab N 跑步 · ./lab fix N 拷解答 · ./lab check 體檢
tutorial.md     # Cloud Shell 教學側欄
common.py       # AgentMall (shop.leapcore.tw) tools — agent 的「手」
helper.py       # 🤖 小助教 agent（載入官方 SDK skill）
steps/          # step1..8（每檔 ≤35 行，頂部 docstring = 目標+checkpoint）＋選做 step9 語音網頁
solutions/      # 完整解答
```

## 📚 官方資源

- SDK: <https://github.com/google-antigravity/antigravity-sdk-python>
- Examples: `examples/getting_started`（單功能）＋ `examples/deep_dives`（進階）
- Skills: `skills/google-antigravity-sdk/`（13 篇給 AI 看的教學 md）

---

執行環境：Python ≥ 3.11，一律用 [`uv`](https://docs.astral.sh/uv/)。
