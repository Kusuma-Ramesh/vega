import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
NAME = os.getenv("VEGA_NAME", "Vega")
MODEL = os.getenv("VEGA_MODEL", "claude-sonnet-5-5")
PORT = int(os.getenv("VEGA_PORT", "8000"))
DATA_DIR = Path.home() / ".vega"
SYSTEM = (
    f"You are {NAME}, a calm, witty personal assistant running on the user's PC. "
    "Your replies are spoken aloud, so keep them short and conversational: "
    "no markdown, no bullet lists, no emoji. Use your tools whenever they help, "
    "and say plainly when something fails."
)
