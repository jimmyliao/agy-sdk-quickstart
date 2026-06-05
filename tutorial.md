# 🚀 Antigravity SDK 八步實戰

歡迎來到 **Build with AI 2026 Taipei**！跟著側欄一步步把你的第一隻生活助理 agent 建出來。
每一步都是：**貼一句指令 → 跑 → 看 checkpoint**。卡住按 `./lab fix N` 拿解答。
（主線 8 步＋一關選做的 step 9「跟你的 agent 說話 🎤」。）

## 步驟 0 · 環境暖機

在終端機跑一次（依賴會在演講時間內背景下載好）：

```bash
./setup.sh
```

接著把 signup 卡片給你的「兩行」貼上（你的 key 與暱稱）：

```bash
export GEMINI_API_KEY=AIza...你的key...
export STUDENT_ID=你的暱稱
```

體檢一下，全部 ✅ 才往下：

```bash
./lab check
```

> 🤖 任何時候卡住，開**第二個分頁**問小助教：`uv run python helper.py`

## 步驟 1 · hello world（中文自介）

```bash
./lab 1
```

✅ checkpoint：agent 用**繁體中文**自我介紹。

## 步驟 2 · streaming（逐字跳出）

```bash
./lab 2
```

✅ checkpoint：文字一個個跳出來，不用乾等。

## 步驟 3 · tools（真的去查商城）✨

```bash
./lab 3
```

✅ checkpoint：問「有耳機嗎？」agent 真的查到 🎧 並報價＋報天氣。這就是魔法時刻。

## 步驟 4 · structured output（要清單不要散文）

```bash
./lab 4
```

✅ checkpoint：印出整齊 JSON，每筆有 品名／價格／推薦理由。

## 步驟 5 · hooks（結帳前停下來問你）🎉

```bash
./lab 5
```

✅ checkpoint：agent 要結帳時跳 `確認嗎？[y/N]` → 按 `y` → **你的訂單跳上投影幕 /wall** 🎉

> 🏁 **結帳賽**：最先「透過 agent」結帳的前幾名有小禮物！（手戳 API 不算，lab 的 checkout 會帶 `X-Via: agent`）

## 步驟 6 · 消費上限 guardrail（optional）

```bash
./lab 6
```

✅ checkpoint：金額 > NT$3000 自動被守門員擋下。時間不夠可跳過。

## 步驟 7 · multimodal（用說的點外送）🍜

```bash
./lab 7
```

✅ checkpoint：語音指令 → agent 聽懂 → 🛵 外送成立。（沒音檔會自動 fallback 成文字）

## 步驟 8 · doc agent（自動產消費報告）🏁

```bash
./lab 8
cat my-life-report.md
```

✅ checkpoint：打開 `my-life-report.md`，agent 幫你寫好今晚消費總結。E2E 完成！

## 步驟 9 · 跟你的 agent 說話（選做炫技）🎤

主線 8 步跑完了！有時間就玩這關——把同一隻 agent 包成一個**手機友善的網頁**，
你直接「按住麥克風講話」就能下指令。

```bash
./lab 9
```

這會啟動一個 web server（uvicorn，0.0.0.0:8080）。**在 Cloud Shell 看畫面**：

1. 視窗右上角點 **「網頁預覽」**（一個小螢幕的 icon）。
2. 選 **「透過以下連接埠預覽」→ 8080**。
3. 瀏覽器分頁就會開出深色的錄音頁。

頁面三條路，由易到難保底：

- **按住 🎤**：錄音 → 放開送出（原生語音多模態）。
- **🗣️ 瀏覽器轉文字**：Chrome 內建 Web Speech API，先辨識成文字再送（保底）。
- **純文字輸入框**：打字也能用（最終保底）。

✅ checkpoint：點開 8080 → 按住 🎤 講「幫我查降噪耳機」→ 看到 agent 的回覆。

> 🎙️ **第一次會跳麥克風權限**，按「允許」。手機上是「按住講、放開送」。
>
> ⚠️ **webm 注意**：瀏覽器多半錄成 `webm/opus`，但 SDK 只收 wav/mp3/ogg/aac/flac/m4a。
> 後端有 `ffmpeg` 會自動轉檔；**沒有 ffmpeg 又錄到 webm 時，畫面會提示你改用「🗣️ 轉文字」按鈕**。
>
> ⚠️ 這關結帳走「**web 自動核可**」（網頁沒終端機按 y/N），agent 想結帳會直接成立，試玩請小心。
>
> 🛑 玩完按 **Ctrl-C** 關掉 server，回去做下面的自由練習。

## 🎓 自由練習：三層階梯

1. **改人設**：改 `system_instructions`，把它變成毒舌管家／台語導購。
2. **改策略**：改 hook，做月底省錢模式／只推 4.8★／比價才結帳。
3. **組合技 / 自帶題**：聚餐統籌（查天氣 + 訂位 + 外送），或帶自己的 use case。

## 📚 回家有路

- 官方 SDK：<https://github.com/google-antigravity/antigravity-sdk-python>
- `examples/getting_started`（單功能）＋ `examples/deep_dives`（進階）
- `skills/google-antigravity-sdk/`（13 篇給 AI 看的教學）
