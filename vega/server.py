"""Web mode: a local server for the HUD. Browser does hearing; Python is the brain."""
import asyncio
from pathlib import Path

from fastapi import FastAPI, Request, Response, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse

from . import tts_clone
from .brain import make_brain
from .config import MODEL, PORT, PROVIDER, USER, google_connected
from .text import speakable, split_reply
from .tools import state

app = FastAPI()
ORIGINS = {f"http://localhost:{PORT}", f"http://127.0.0.1:{PORT}"}
PAGE = Path(__file__).resolve().parent.parent / "web" / "index.html"


@app.get("/")
def index():
    return FileResponse(PAGE)


@app.get("/config")
def config():
    return {"user": USER, "clone": tts_clone.available(), "google": google_connected(),
            "provider": PROVIDER, "model": MODEL}


@app.post("/speak")
async def speak(req: Request):
    if req.headers.get("origin") not in ORIGINS:
        return Response(status_code=403)
    body = await req.json()
    lang = body.get("lang", "en")
    if lang not in tts_clone.LANGS:
        return Response(status_code=415)  # the clone can't speak this language; browser voice is used
    text = speakable(body.get("text", ""))[:600]
    try:
        return Response(await asyncio.to_thread(tts_clone.synth, text, lang), media_type="audio/wav")
    except Exception as e:
        print(f"[voice clone] {e}")
        return Response(status_code=500)


@app.websocket("/ws")
async def ws(sock: WebSocket):
    # Only our own page may talk to the brain (stops other websites hijacking it).
    if sock.headers.get("origin") not in ORIGINS:
        await sock.close(code=1008)
        return
    await sock.accept()
    loop = asyncio.get_running_loop()

    def emit(kind, data):
        asyncio.run_coroutine_threadsafe(sock.send_json({"type": kind, **data}), loop)

    state["notify"] = lambda m: emit("notice", {"text": m})
    brain = make_brain(on_event=emit)
    try:
        while True:
            text = (await sock.receive_json()).get("text", "").strip()
            if not text:
                continue
            try:
                reply = await asyncio.to_thread(brain.ask, text)
                display, spoken = split_reply(reply)
                await sock.send_json({"type": "reply", "text": display, "say": spoken})
            except Exception as e:
                await sock.send_json({"type": "error", "text": str(e)})
    except WebSocketDisconnect:
        pass
