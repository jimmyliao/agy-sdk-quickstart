# agy-sdk-quickstart 🚀

> Build your first AI agent with the **Antigravity SDK** — ~50 minutes, zero install, bring your own free key.

用 Antigravity SDK 一步步建出一隻**生活助理 agent**：查商品、加購物車、**結帳前停下來問你**、叫外送、最後自動產出一份消費報告。所有 agent 連到同一個 mock 商城 `shop.leapcore.tw`，訂單即時跳上一面共享投影牆 `/wall` 🎉

原為 [Build with AI 2026 Taipei](https://jimmyliao.pse.is/bwai0616) 的 codelab，現已開源 —— **自己帶一把免費金鑰就能跑**。

## Quick start

```bash
git clone https://github.com/jimmyliao/agy-sdk-quickstart
cd agy-sdk-quickstart
./setup.sh                          # uv + 依賴 + 商城連線檢查

# 拿一把免費金鑰：https://ai.dev/apikey （Create API key）
export GEMINI_API_KEY=AIza...你的金鑰...
export STUDENT_ID=yourname           # 任意英數，當作你的身分（上牆顯示）
./lab save                           # （選）存起來，免得每次重貼

./lab                                # 直接跟 agent 對話
```

打一句「幫我找一個降噪耳機，然後結帳」，你會看到 agent 怎麼運作的 **三層鏈**：

```
🔧 agent 決定用工具：search_products(q='降噪耳機')    ← SDK 在編排
   🌐 GET  /products → ✅ 200 · 64ms                 ← 真的打商城
🔧 agent 決定用工具：checkout()
   🌐 POST /checkout → ✅ 200                        ← 訂單成立，跳上 /wall
🤖 已為您找到 Sony WH-1000XM5 並完成結帳。            ← agent 回你
```

## 想學怎麼自己建？8 步漸進

`./lab` 給你一隻現成的 agent 玩；想學怎麼建，`./lab 1` 開始，一步一個 SDK 能力：

| # | step | 學到的 SDK 能力 |
|---|------|----------------|
| 1 | hello | 建 `Agent`、對話 |
| 2 | streaming | 逐字串流輸出 |
| 3 | tools | function = agent 的「手」（查商城）|
| 4 | structured | 拿到結構化 JSON |
| 5 | **hooks** ⭐ | `pre_tool_call_decide` 結帳前人工核可（human-in-the-loop）|
| 6 | guardrail | 消費上限攔截 |
| 7 | multimodal | 語音點外送 |
| 8 | doc agent | agent 自動寫報告檔 |
| 9 | voice web（選做）| 按住麥克風跟 agent 說話（FastAPI + 瀏覽器）|

`./lab fix N` 卡住拷解答 · `./lab check` 環境體檢 · `uv run python helper.py` 問 AI 小助教（用 agent 學 agent）

## 結構

```
lab             # CLI 入口：./lab（玩）· N（學）· check · save · fix N
play.py         # 互動 agent（./lab 預設）
common.py       # mock 商城 tools = agent 的「手」
trace_hooks.py  # 三層鏈可視化 hooks
steps/          # step1–9（每檔精簡，docstring = 目標 + checkpoint）
solutions/      # 完整解答
helper.py       # AI 小助教
```

## 需要

- Python ≥ 3.11 + [`uv`](https://docs.astral.sh/uv/)
- 一把免費 Gemini API key → **[ai.dev/apikey](https://ai.dev/apikey)**
  - ⚠️ 免費層每分鐘有呼叫上限（~10–15 RPM）。一個請求 agent 會想好幾步，連續快玩容易撞到——慢慢來、或等 30–60 秒即可。

## See also

- [agy-cli-quickstart](https://github.com/jimmyliao/agy-cli-quickstart) — CLI 版 lab（@ BWAI Tainan）
- Antigravity SDK：`pip install google-antigravity`

---

Apache-2.0 · by [Jimmy Liao](https://github.com/jimmyliao)（Google Cloud AI GDE）
