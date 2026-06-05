"""Step 9 · voice web（選做炫技）— 「跟你的 agent 說話」🎤.

目標：開一個手機友善的網頁，**按住麥克風講話** → 同一隻生活助理 agent
聽懂後查商品／加購物車／結帳／叫外送，回覆顯示在畫面上。
在 Cloud Shell 跑起來後，點右上「網頁預覽 → 透過以下連接埠預覽 8080」即可開。

checkpoint：手機/瀏覽器點開 8080 → 按住 🎤 講「幫我買降噪耳機」→ 看到 agent 回覆。

設計重點（給想看 code 的同學）：
  - 單檔 FastAPI/Starlette app，uvicorn 跑 0.0.0.0:8080。
  - 一隻「常駐 agent」：app 啟動時 __aenter__ 起來，所有請求共用同一段對話。
  - 三條輸入路徑，由易到難保底：
      1) 主模式：MediaRecorder 錄音 → POST /voice → ag.types.Audio 餵 agent。
      2) fallback：瀏覽器 Web Speech API 轉文字 → POST /chat。
      3) 保底：純文字輸入框 → POST /chat。
  - 結帳核可 hook：web 沒有終端機可以按 y/N，所以這裡改成「自動放行 +
    在回覆裡附註『web 模式自動核可』」，並在頁面掛一條警語。
  - ⚠️ 瀏覽器 MediaRecorder 多半錄成 webm/opus，但 SDK 的 Audio 只收
    wav/mp3/ogg/aac/flac/m4a 這幾種 mime，**不收 webm**。所以後端會：
      a) 前端優先嘗試錄 audio/ogg;codecs=opus（部分瀏覽器支援）；
      b) 收到 webm 時，若機器有 ffmpeg → 轉成 ogg/opus 再餵；
      c) 沒有 ffmpeg 又是 webm → 回一句友善提示，請改用 🗣️ 轉文字按鈕。

卡住就：./lab fix 9
"""
import contextlib
import os
import pathlib
import shutil
import subprocess
import uuid

import google.antigravity as ag
from google.antigravity import types
from google.antigravity.hooks import hooks

# 用 Starlette（FastAPI 的底層）：它已隨 SDK 的 uvicorn 依賴進來，不用多裝 fastapi。
# 寫法跟 FastAPI 幾乎一樣，路由 + async handler + lifespan。
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Route

from common import (
    add_to_cart,
    book_table,
    cart_total,
    checkout,
    get_weather,
    order_food,
    search_products,
    view_cart,
)

REPO = pathlib.Path(__file__).resolve().parent.parent
INBOX = REPO / "assets"  # 入站語音檔存這裡（沿用既有 assets/）

# SDK 的 Audio 接受的副檔名 → mime（webm 不在內，必須轉檔）
EXT_MIME = {
    ".ogg": "audio/ogg",
    ".oga": "audio/ogg",
    ".opus": "audio/ogg",
    ".mp3": "audio/mp3",
    ".m4a": "audio/m4a",
    ".mp4": "audio/m4a",
    ".aac": "audio/aac",
    ".flac": "audio/flac",
    ".wav": "audio/wav",
}
HAS_FFMPEG = shutil.which("ffmpeg") is not None


# ── 結帳核可 hook：web 版沒有終端機，改自動放行 + 附註 ──────────────────
@hooks.pre_tool_call_decide
async def web_auto_approve(data: types.ToolCall) -> types.HookResult:
    if data.name == "checkout":
        # 想更保守可在這裡 allow=False 擋下，但 demo 走自動核可比較順
        return types.HookResult(
            allow=True, message="（web 模式自動核可結帳；正式場合請改為人工確認）"
        )
    return types.HookResult(allow=True)


def build_agent() -> ag.Agent:
    cfg = ag.LocalAgentConfig(
        system_instructions=(
            "你是繁體中文的生活助理。使用者會用語音或文字下指令，"
            "請依需求呼叫工具：查商品(search_products)、查天氣(get_weather)、"
            "加購物車(add_to_cart)、看購物車(view_cart)、結帳(checkout)、"
            "叫外送(order_food, r01=拉麵 r03=壽司 r04=牛肉麵)、訂位(book_table)。"
            "回覆精簡、口語、適合在手機上閱讀。"
        ),
        tools=[
            search_products,
            get_weather,
            add_to_cart,
            view_cart,
            checkout,
            order_food,
            book_table,
        ],
        hooks=[web_auto_approve],
        model="gemini-flash-latest",
        api_key=os.environ["GEMINI_API_KEY"],
        workspaces=[os.getcwd()],
    )
    return ag.Agent(cfg)


# 常駐 agent（app 啟動時 __aenter__、關閉時 __aexit__）
AGENT: ag.Agent | None = None


@contextlib.asynccontextmanager
async def lifespan(app: Starlette):
    """app 生命週期：開機建一隻常駐 agent，所有請求共用同一段對話；關機收尾。"""
    global AGENT
    if not os.environ.get("GEMINI_API_KEY"):
        raise RuntimeError("沒設 GEMINI_API_KEY，先 export 再跑 ./lab 9")
    INBOX.mkdir(parents=True, exist_ok=True)
    AGENT = build_agent()
    await AGENT.__aenter__()
    print("🎤 voice agent 已就緒。Cloud Shell：右上『網頁預覽 → 連接埠 8080』")
    if not HAS_FFMPEG:
        print("ℹ️ 沒偵測到 ffmpeg：webm 錄音將無法直接送，請用『🗣️ 轉文字』按鈕保底。")
    try:
        yield
    finally:
        await AGENT.__aexit__(None, None, None)


# ── 音檔處理：存檔 → 必要時轉成 ogg/opus → 回 (path, mime) ──────────────
def _ext_from_content_type(ct: str, filename: str) -> str:
    ct = (ct or "").lower()
    if filename and "." in filename:
        return "." + filename.rsplit(".", 1)[-1].lower()
    if "ogg" in ct:
        return ".ogg"
    if "mp4" in ct or "m4a" in ct or "aac" in ct:
        return ".m4a"
    if "mpeg" in ct or "mp3" in ct:
        return ".mp3"
    if "wav" in ct:
        return ".wav"
    if "webm" in ct:
        return ".webm"
    return ".bin"


def save_and_prepare(raw: bytes, content_type: str, filename: str) -> tuple[pathlib.Path, str] | None:
    """存入站語音、必要時轉檔。回 (路徑, mime)；無法處理回 None。"""
    ext = _ext_from_content_type(content_type, filename)
    stamp = uuid.uuid4().hex[:8]
    saved = INBOX / f"voice-{stamp}{ext}"
    saved.write_bytes(raw)

    if ext in EXT_MIME:
        return saved, EXT_MIME[ext]

    # webm（或其他不支援）→ 有 ffmpeg 就轉 ogg/opus（opus 已在 webm 內，重包即可）
    if HAS_FFMPEG:
        out = INBOX / f"voice-{stamp}.ogg"
        try:
            subprocess.run(
                ["ffmpeg", "-y", "-i", str(saved), "-c:a", "libopus", "-f", "ogg", str(out)],
                check=True, capture_output=True, timeout=30,
            )
            return out, "audio/ogg"
        except Exception as e:
            print(f"⚠️ ffmpeg 轉檔失敗：{e}")
            return None
    return None  # 沒 ffmpeg 又是 webm → 交給前端 fallback


# ── 路由 ────────────────────────────────────────────────────────────────
async def index(request: Request) -> HTMLResponse:
    return HTMLResponse(PAGE)


async def voice(request: Request) -> JSONResponse:
    form = await request.form()
    up = form.get("audio")
    if up is None:
        return JSONResponse({"ok": False, "reply": "沒收到音檔。"}, status_code=400)
    raw = await up.read()
    prepared = save_and_prepare(raw, up.content_type or "", up.filename or "")
    if prepared is None:
        return JSONResponse({
            "ok": False,
            "reply": "這台機器沒有 ffmpeg，無法處理瀏覽器的 webm 錄音 🥲\n"
                     "請改用下方『🗣️ 瀏覽器轉文字』按鈕，或用文字輸入框。",
        })
    path, mime = prepared
    # 不直接用 Audio.from_file（它靠副檔名猜 mime，wav→audio/x-wav 會被 SDK 退件）；
    # 改用我們判定好的 mime 自己建 Audio，最穩。
    audio = types.Audio(data=path.read_bytes(), mime_type=mime)
    r = await AGENT.chat(["這是我的語音指令，請照辦：", audio])
    return JSONResponse({"ok": True, "reply": await r.text()})


async def chat(request: Request) -> JSONResponse:
    data = await request.json()
    text = (data.get("text") or "").strip()
    if not text:
        return JSONResponse({"ok": False, "reply": "請說點什麼 🙂"})
    r = await AGENT.chat(text)
    return JSONResponse({"ok": True, "reply": await r.text()})


async def orders(request: Request) -> JSONResponse:
    """方便 demo / 驗證：看目前購物車狀態。"""
    return JSONResponse(view_cart())


app = Starlette(
    routes=[
        Route("/", index),
        Route("/voice", voice, methods=["POST"]),
        Route("/chat", chat, methods=["POST"]),
        Route("/orders", orders),
    ],
    lifespan=lifespan,
)


# ── 前端：一頁深色、行動友善的錄音頁（zh-TW）────────────────────────────
PAGE = """<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
<title>🎤 跟你的 agent 說話</title>
<style>
  :root { color-scheme: dark; }
  * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
  body { margin:0; font-family:-apple-system,"PingFang TC","Noto Sans TC",system-ui,sans-serif;
         background:#0d1117; color:#e6edf3; min-height:100vh; display:flex; flex-direction:column;
         align-items:center; padding:20px; }
  h1 { font-size:20px; margin:8px 0 2px; }
  .sub { color:#8b949e; font-size:13px; margin-bottom:14px; text-align:center; }
  .warn { background:#3d2b00; color:#f0c674; border:1px solid #5a4100; border-radius:10px;
          padding:8px 12px; font-size:12px; margin-bottom:14px; max-width:420px; text-align:center; }
  #mic { width:160px; height:160px; border-radius:50%; border:none; font-size:56px;
         background:#238636; color:#fff; box-shadow:0 8px 24px rgba(35,134,54,.4);
         transition:transform .08s, background .15s; user-select:none; touch-action:none; }
  #mic:active, #mic.rec { transform:scale(.94); background:#da3633;
         box-shadow:0 8px 24px rgba(218,54,51,.5); }
  .hint { color:#8b949e; font-size:13px; margin:12px 0; }
  .row { display:flex; gap:8px; width:100%; max-width:420px; margin:8px 0; }
  button.alt { flex:1; padding:12px; border-radius:10px; border:1px solid #30363d;
               background:#161b22; color:#e6edf3; font-size:15px; }
  button.alt:active { background:#21262d; }
  input#txt { flex:1; padding:12px; border-radius:10px; border:1px solid #30363d;
              background:#0d1117; color:#e6edf3; font-size:16px; }
  #send { padding:12px 16px; border-radius:10px; border:none; background:#1f6feb; color:#fff; font-size:15px; }
  #reply { width:100%; max-width:420px; background:#161b22; border:1px solid #30363d;
           border-radius:12px; padding:14px; margin-top:14px; min-height:60px; white-space:pre-wrap;
           line-height:1.6; font-size:15px; }
  .me { color:#58a6ff; }
  .status { color:#8b949e; font-size:12px; height:16px; margin-top:6px; }
.chip{background:#1e293b;border:1px solid #334155;color:#cbd5e1;border-radius:14px;padding:5px 10px;font-size:.78rem;cursor:pointer}.chip:hover{border-color:#60a5fa;color:#fff}
</style>
</head>
<body>
  <h1>🎤 跟你的 agent 說話</h1>
  <div class="sub">按住下面的麥克風講話，放開就送出給你的生活助理 agent</div>
  <div class="warn">⚠️ 結帳採「web 自動核可」：agent 想結帳會直接成立，請小心試玩。</div>

  <button id="mic" aria-label="按住錄音">🎤</button>
  <div class="hint" id="hint">按住 🎤 開始錄，放開送出</div>
  <div class="status" id="status"></div>

  <div class="row">
    <button class="alt" id="speech">🗣️ 瀏覽器轉文字（保底）</button>
  </div>
  <div class="row">
    <div class="chips" style="display:flex;gap:6px;flex-wrap:wrap;margin:8px 0">
      <button type="button" class="chip" onclick="useChip(this)">外面下大雨，看有沒有雨衣，順便來份火鍋外送</button>
      <button type="button" class="chip" onclick="useChip(this)">推薦健康食品裡值得買的，講一下為什麼</button>
      <button type="button" class="chip" onclick="useChip(this)">幫我找筆電架，預算一千以內</button>
      <button type="button" class="chip" onclick="useChip(this)">週五晚上七點半訂壽司店四個位子</button>
    </div>
    <input id="txt" placeholder="或直接打字，例如：幫我查耳機" />
    <button id="send">送出</button>
  </div>

  <div id="reply">（agent 的回覆會出現在這裡）</div>

<script>
function useChip(b){const t=document.getElementById('txt');t.value=b.textContent;t.focus();}

const $ = (id) => document.getElementById(id);
const replyBox = $("reply"), statusEl = $("status");
function setStatus(s){ statusEl.textContent = s || ""; }
function showReply(text){ replyBox.textContent = text; }
function showMine(text){ replyBox.innerHTML = '<span class="me">你：' + text + '</span>\\n\\n⏳ agent 思考中…'; }

// ── 主模式：MediaRecorder 按住錄、放開送 ──────────────────────────────
let mediaRecorder = null, chunks = [], stream = null, mimeUsed = "";
// 優先挑 SDK 收得下的格式（ogg/opus）；多數 Chromium 只給 webm，後端會試著轉檔
function pickMime(){
  const prefs = ["audio/ogg;codecs=opus","audio/ogg","audio/webm;codecs=opus","audio/webm","audio/mp4"];
  for (const m of prefs){ if (window.MediaRecorder && MediaRecorder.isTypeSupported(m)) return m; }
  return "";
}
async function ensureStream(){
  if (stream) return stream;
  stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  return stream;
}
async function startRec(){
  try {
    await ensureStream();
    mimeUsed = pickMime();
    mediaRecorder = mimeUsed ? new MediaRecorder(stream, { mimeType: mimeUsed })
                             : new MediaRecorder(stream);
    chunks = [];
    mediaRecorder.ondataavailable = (e) => { if (e.data.size) chunks.push(e.data); };
    mediaRecorder.onstop = sendRecording;
    mediaRecorder.start();
    $("mic").classList.add("rec");
    setStatus("錄音中…（" + (mimeUsed || "預設") + "）");
  } catch (err) {
    setStatus("拿不到麥克風權限 😢 用下面的轉文字或打字");
  }
}
function stopRec(){
  if (mediaRecorder && mediaRecorder.state !== "inactive"){
    mediaRecorder.stop();
    $("mic").classList.remove("rec");
    setStatus("送出中…");
  }
}
async function sendRecording(){
  if (!chunks.length){ setStatus("沒錄到聲音"); return; }
  const blob = new Blob(chunks, { type: mimeUsed || "audio/webm" });
  const ext = (mimeUsed.includes("ogg") ? "ogg" : mimeUsed.includes("mp4") ? "m4a" : "webm");
  const fd = new FormData();
  fd.append("audio", blob, "rec." + ext);
  showMine("🎤（語音）");
  try {
    const res = await fetch("/voice", { method:"POST", body: fd });
    const j = await res.json();
    showReply(j.reply || "(沒有回覆)");
  } catch (e) { showReply("送出失敗：" + e); }
  setStatus("");
}
// 滑鼠 + 觸控都支援「按住錄、放開送」
const mic = $("mic");
mic.addEventListener("mousedown", startRec);
mic.addEventListener("mouseup", stopRec);
mic.addEventListener("mouseleave", () => { if (mic.classList.contains("rec")) stopRec(); });
mic.addEventListener("touchstart", (e)=>{ e.preventDefault(); startRec(); }, {passive:false});
mic.addEventListener("touchend",  (e)=>{ e.preventDefault(); stopRec();  }, {passive:false});

// ── fallback：Web Speech API 轉文字（Chrome 內建）────────────────────
$("speech").addEventListener("click", () => {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR){ setStatus("這個瀏覽器沒有語音轉文字，請改打字"); return; }
  const rec = new SR();
  rec.lang = "zh-TW"; rec.interimResults = false; rec.maxAlternatives = 1;
  setStatus("🗣️ 請說話…");
  rec.onresult = (e) => { const t = e.results[0][0].transcript; $("txt").value = t; sendText(t); };
  rec.onerror = (e) => setStatus("辨識失敗：" + e.error);
  rec.onend = () => setStatus("");
  rec.start();
});

// ── 保底：純文字 ────────────────────────────────────────────────────
async function sendText(text){
  text = (text || $("txt").value || "").trim();
  if (!text) return;
  showMine(text);
  try {
    const res = await fetch("/chat", {
      method:"POST", headers:{ "Content-Type":"application/json" },
      body: JSON.stringify({ text }) });
    const j = await res.json();
    showReply(j.reply || "(沒有回覆)");
  } catch (e){ showReply("送出失敗：" + e); }
  $("txt").value = "";
}
$("send").addEventListener("click", () => sendText());
$("txt").addEventListener("keydown", (e) => { if (e.key === "Enter") sendText(); });
</script>
</body>
</html>"""


if __name__ == "__main__":
    import uvicorn

    # Cloud Shell 網頁預覽走 8080；0.0.0.0 讓預覽 proxy 進得來
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
