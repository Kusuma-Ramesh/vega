"""Optional: speak in YOUR voice using XTTS-v2 (free, runs on your PC).
Setup: pip install -r requirements-clone.txt, then put a clean 10-30 second recording of
your voice at voice/me.wav. Without that file Vega uses the browser voice instead."""
import os
import tempfile
import threading
from pathlib import Path

REF = Path(__file__).resolve().parent.parent / "voice" / "me.wav"
_tts, _lock = None, threading.Lock()


def available() -> bool:
    return REF.exists()


def synth(text: str) -> bytes:
    global _tts
    with _lock:  # one sentence at a time; the first call loads the model (slow)
        if _tts is None:
            from TTS.api import TTS
            _tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        tmp.close()
        try:
            _tts.tts_to_file(text=text, speaker_wav=str(REF), language="en", file_path=tmp.name)
            return Path(tmp.name).read_bytes()
        finally:
            os.unlink(tmp.name)
