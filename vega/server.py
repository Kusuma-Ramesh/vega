"""Web mode: a local server for the HUD. Browser does hearing; Python is the brain."""
import asyncio
import re
from pathlib import Path

from fastapi import FastAPI, Request, Response, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse

from . import tts_clone
from .brain import make_brain
from .config import PORT, USER
from .tools import state

app = FastAPI()
ORIGINS = {f"http://localhost:{PORT}", f"http://127.0.0.1:{PORT}"}
PAGE = Path(__file__).resolve().parent.parent / "web" / "index.html"


def clean(text: str) -> str:
    return re.sub(r"[*_`#]+", "", text).strip()  # models love markdown; speech does not


@app.get("/")
def index():
    return FileResponse(PAGE)


@app.get("/config")
def config():
    return {"user": USER, "clone": tts_clone.available()}


@app.post("/speak")
async def speak(req: Request):
    if req.headers.get("origin") not in ORIGINS:
        return Response(status_code=403)
    text = clean((await req.json()).get("text", ""))[:600]
    try:
        return Response(await asyncio.to_thread(tts_clone.synth, text), media_type="audio/wav")
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
                await sock.send_json({"type": "reply", "text": clean(reply)})
            except Exception as e:
                await sock.send_json({"type": "error", "text": str(e)})
    except WebSocketDisconnect:
        pass
