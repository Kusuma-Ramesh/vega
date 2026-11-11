"""Web mode: a local server for the HUD. Browser does hearing/speaking; Python is the brain."""
import asyncio
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse

from .brain import Brain
from .config import PORT
from .tools import state

app = FastAPI()
ORIGINS = {f"http://localhost:{PORT}", f"http://127.0.0.1:{PORT}"}
PAGE = Path(__file__).resolve().parent.parent / "web" / "index.html"


@app.get("/")
def index():
    return FileResponse(PAGE)


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
    brain = Brain(on_event=emit)
    try:
        while True:
            text = (await sock.receive_json()).get("text", "").strip()
            if not text:
                continue
            try:
                reply = await asyncio.to_thread(brain.ask, text)
                await sock.send_json({"type": "reply", "text": reply})
            except Exception as e:
                await sock.send_json({"type": "error", "text": str(e)})
    except WebSocketDisconnect:
        pass
