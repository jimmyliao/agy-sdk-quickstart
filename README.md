# agy-sdk-quickstart 🚀

**Build with AI 2026 Taipei — Antigravity SDK 實戰：在 Cloud Shell 上建出你的第一個 AI Agent**
6/16 (Tue) 19:00–21:30 · CAAM 承德168

> 🚧 Workshop 教材建置中，活動當天轉為 public。
> （sibling repo: [agy-cli-quickstart](https://github.com/jimmyliao/agy-cli-quickstart) — CLI 版 lab @ BWAI Tainan 2026-05-23）

## 規劃結構
```
setup.sh        # 環境一鍵就緒（uv / 依賴暖機 / shop 連線檢查）
lab             # ./lab 3 跑步 · ./lab fix 3 拷解答 · ./lab check 體檢
tutorial.md     # Cloud Shell 教學側欄
common.py       # AgentMall (shop.leapcore.tw) tools
helper.py       # 🤖 小助教 agent（載入官方 SDK skill）
steps/          # step1..8（每檔 ≤30 行）
solutions/      # 完整解答
```

## 官方資源
- SDK: https://github.com/google-antigravity/antigravity-sdk-python
- Examples: `examples/getting_started` + `examples/deep_dives`
