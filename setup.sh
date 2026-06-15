#!/usr/bin/env bash
# setup.sh — 環境一鍵就緒（uv / 依賴暖機 / shop 連線檢查）
# 設計成在 Part 1 演講的 30 分鐘內背景跑完。
set -euo pipefail
cd "$(dirname "$0")"
SHOP="${SHOP_URL:-https://shop.leapcore.tw}"

echo "🚀 agy-sdk-quickstart 環境暖機中…"
echo "────────────────────────────────────────"

# 1) 確認 / 安裝 uv（Cloud Shell 多半已內建）
if command -v uv >/dev/null 2>&1; then
  echo "✅ uv 已安裝（$(uv --version)）"
else
  echo "📦 安裝 uv…"
  curl -LsSf https://astral.sh/uv/install.sh | sh
  # 把這次 session 的 PATH 補上
  export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
  command -v uv >/dev/null 2>&1 && echo "✅ uv 安裝完成（$(uv --version)）" \
    || { echo "❌ uv 安裝失敗，請手動安裝後重跑 ./setup.sh"; exit 1; }
fi

# 2) 暖快取：把依賴抓下來建好 venv（之後跑 step 就秒開）
echo "📦 下載依賴並建立虛擬環境（首次需要一點時間）…"
uv sync 2>/dev/null || uv pip install -q google-antigravity httpx
echo "✅ 依賴就緒"

# 3) 連線檢查商城
echo "🌐 檢查商城 $SHOP …"
if curl -fsS --max-time 8 "$SHOP/health" >/dev/null 2>&1; then
  echo "✅ 商城連得上"
else
  echo "⚠️  暫時連不到商城（可能網路或上游），稍後 ./lab check 再確認一次"
fi

chmod +x ./lab 2>/dev/null || true

echo "────────────────────────────────────────"
echo "✅ 環境就緒！接下來："
echo ""
echo "  1️⃣  拿一把免費金鑰：https://ai.dev/apikey （Create API key）"
echo "      貼上這兩行（STUDENT_ID 用報到頁的 u0xx）："
echo "        export GEMINI_API_KEY=AIza...你的金鑰..."
echo "        export STUDENT_ID=u0xx"
echo "        ./lab save        # 存起來，斷線不用再貼"
echo ""
echo "  2️⃣  體檢： ./lab check    （key / 商城 / SDK 都要 ✅）"
echo ""
echo "  3️⃣  開玩： ./lab          （直接跟 agent 說話）"
echo "             想自己動手建？ ./lab 1 起，一步一個 SDK 能力"
echo ""
echo "  🤖 卡住了？開第二個分頁問小助教：uv run python helper.py"
echo "────────────────────────────────────────"
