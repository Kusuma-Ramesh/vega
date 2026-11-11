"""Safe, read-mostly tools: time, weather, web search, notes."""
import urllib.parse
import urllib.request
from datetime import datetime

from ..config import DATA_DIR
from .registry import tool

NOTES = DATA_DIR / "notes.txt"


@tool
def get_time() -> str:
    """Get the current local date and time."""
    return datetime.now().strftime("%A, %d %B %Y, %I:%M %p")


@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    url = "https://wttr.in/" + urllib.parse.quote(city) + "?format=3"
    return urllib.request.urlopen(url, timeout=8).read().decode()


@tool
def web_search(query: str) -> str:
    """Search the web and return the top results."""
    from ddgs import DDGS
    hits = DDGS().text(query, max_results=4)
    return "\n".join(f"{h['title']}: {h['body']}" for h in hits) or "No results."


@tool
def take_note(text: str) -> str:
    """Save a note for the user."""
    DATA_DIR.mkdir(exist_ok=True)
    with NOTES.open("a", encoding="utf-8") as f:
        f.write(f"[{datetime.now():%Y-%m-%d %H:%M}] {text}\n")
    return "Note saved."


@tool
def read_notes() -> str:
    """Read back the user's saved notes."""
    return NOTES.read_text(encoding="utf-8") if NOTES.exists() else "No notes yet."
