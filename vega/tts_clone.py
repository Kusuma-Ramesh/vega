"""Optional: speak in YOUR voice using XTTS-v2 (free, runs on your PC).
Setup: pip install -r requirements-clone.txt, record voice/me.wav (python -m vega record-voice),
then run python -m vega clone-setup once. Without these Vega uses the browser voice instead.
XTTS-v2 can speak English and Hindi among others, but NOT Kannada, Telugu, Tamil, Malayalam and
the other Indian languages. For those, Vega falls back to the browser voice automatically."""
import os
import tempfile
import threading
from pathlib import Path

from .config import DATA_DIR

REF = Path(__file__).resolve().parent.parent / "voice" / "me.wav"
READY = DATA_DIR / "clone_ready"   # created by `python -m vega clone-setup` after you accept the licence
MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"
LANGS = {"en", "hi"}               # languages we send to the clone
_tts, _lock = None, threading.Lock()


def available() -> bool:
    return REF.exists() and READY.exists()


def load_model():
    from TTS.api import TTS
    tts = TTS(MODEL_NAME)
    try:
        import torch
        if torch.cuda.is_available():
            tts.to("cuda")
    except Exception:
        pass
    return tts


def synth(text: str, lang: str = "en") -> bytes:
    global _tts
    if not available():
        raise RuntimeError("Voice clone is not set up. Run: python -m vega clone-setup")
    with _lock:  # one sentence at a time; the first call loads the model (slow)
        if _tts is None:
            _tts = load_model()
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        tmp.close()
        try:
            _tts.tts_to_file(text=text, speaker_wav=str(REF), language=lang, file_path=tmp.name)
            return Path(tmp.name).read_bytes()
        finally:
            os.unlink(tmp.name)
