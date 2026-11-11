"""Helpers for voice cloning: record your voice, and a one-time model setup you run by hand."""
import sys

from .config import DATA_DIR
from .tts_clone import READY, REF, load_model

RATE = 22050
PASSAGE = (
    "Hello, this is my voice. I am recording a short sample so my assistant can speak like me. "
    "The quick brown fox jumps over the lazy dog, and then walks quietly back home. "
    "Today the weather is pleasant, and I feel calm, clear and ready to get things done."
)


def record(seconds: int = 20):
    try:
        import numpy as np
        import sounddevice as sd
    except ImportError:
        raise SystemExit("Run this first:  pip install sounddevice")
    import time
    import wave
    print("\nFind a quiet room. Hold the mic about a hand away. Read this aloud, naturally:\n")
    print(f'  "{PASSAGE}"\n')
    input(f"Press Enter, then read for {seconds} seconds... ")
    for n in (3, 2, 1):
        print(n, end=" ", flush=True)
        time.sleep(1)
    print("\nRECORDING...")
    audio = sd.rec(int(seconds * RATE), samplerate=RATE, channels=1, dtype="int16")
    sd.wait()
    peak = int(np.abs(audio).max())
    REF.parent.mkdir(exist_ok=True)
    with wave.open(str(REF), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(audio.tobytes())
    print(f"Saved {REF}")
    if peak < 3000:
        print("It sounds very quiet. Move closer to the mic and run this again.")
    elif peak > 32000:
        print("It may be too loud (clipping). Move back a little and run this again.")
    else:
        print("Level looks good.")


def setup():
    v = sys.version_info
    print(f"Python {v.major}.{v.minor}.{v.micro}")
    if not (3, 10) <= (v.major, v.minor) <= (3, 12):
        raise SystemExit("coqui-tts needs Python 3.10, 3.11 or 3.12. See the steps for installing one of those.")
    if not REF.exists():
        raise SystemExit(f"No voice sample yet. Run:  python -m vega record-voice   (saves {REF})")
    try:
        import TTS  # noqa: F401
    except ImportError:
        raise SystemExit("Run this first:  pip install -r requirements-clone.txt")
    print("\nThe XTTS-v2 voice model is free for NON-COMMERCIAL use under the Coqui Public Model License")
    print("(https://coqui.ai/cpml). It will now ask you to accept it, then download (~2 GB).\n")
    tts = load_model()  # asks for the licence in this terminal and downloads
    test = REF.parent / "test.wav"
    print("Making a test sentence (the first one is slow)...")
    tts.tts_to_file(text="Hello, this is my voice, speaking through Vega.", speaker_wav=str(REF),
                    language="en", file_path=str(test))
    DATA_DIR.mkdir(exist_ok=True)
    READY.write_text("ok", encoding="utf-8")
    print(f"\nDone. Play {test} to hear it. Restart Vega to use your voice.")
