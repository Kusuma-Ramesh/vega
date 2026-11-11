import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
NAME = os.getenv("VEGA_NAME", "Vega")
PORT = int(os.getenv("VEGA_PORT", "8000"))
DATA_DIR = Path.home() / ".vega"

# provider -> (base url, default model, name of the env var holding the key)
PRESETS = {
    "groq": ("https://api.groq.com/openai/v1", "openai/gpt-oss-120b", "GROQ_API_KEY"),
    "gemini": ("https://generativelanguage.googleapis.com/v1beta/openai/", "gemini-2.5-flash", "GEMINI_API_KEY"),
    "ollama": ("http://localhost:11434/v1", "llama3.1", ""),   # runs on your PC, no key
    "anthropic": (None, "claude-sonnet-5-5", "ANTHROPIC_API_KEY"),  # paid
}
PROVIDER = os.getenv("VEGA_PROVIDER", "groq").lower()
if PROVIDER not in PRESETS:
    raise SystemExit(f"VEGA_PROVIDER must be one of: {', '.join(PRESETS)} (got '{PROVIDER}')")
_url, _model, _keyvar = PRESETS[PROVIDER]
BASE_URL = os.getenv("VEGA_BASE_URL", _url)
MODEL = os.getenv("VEGA_MODEL", _model)
API_KEY = os.getenv("VEGA_API_KEY") or (os.getenv(_keyvar) if _keyvar else "ollama")

USER = os.getenv("VEGA_USER", "")
SYSTEM = (
    f"You are {NAME}, a personal AI assistant in the spirit of JARVIS: dry, quietly witty, "
    "unfailingly competent and loyal. "
    + (f"The user's name is {USER}; use it now and then, not in every sentence. " if USER else "")
    + "Your replies are spoken aloud: one to three short sentences of plain speech, with no markdown, "
    "asterisks, lists or emoji. Act first and talk less: when asked to do something, use a tool, then "
    "confirm in a few words. Offer a next step only when it is obviously useful. Never claim an action "
    "you did not perform; if a tool fails or you lack a capability, say so briefly."
)
