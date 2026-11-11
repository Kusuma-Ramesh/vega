"""Safe, read-mostly tools: time, weather, web search, news, notes, remembered facts."""
import urllib.parse
import urllib.request
from datetime import datetime

from ..config import DATA_DIR, FACTS
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
    """Search the web for current information and return the top results with their sources.
    Use this for anything recent or that may have changed. Answer from these results; do not open pages."""
    from ddgs import DDGS
    try:
        hits = DDGS().text(query, max_results=6)
    except Exception as e:
        return f"Search failed: {e}"
    return "\n".join(f"[{h.get('title', '')}] {h.get('body', '')} (source: {h.get('href', '')})"
                     for h in hits) or "No results."


@tool
def news_search(query: str) -> str:
    """Search recent news stories (headline, source, date and summary). Use this for news questions
    such as 'what's happening with ...' or 'latest news on ...'. Summarise the stories; do not open pages."""
    from ddgs import DDGS
    try:
        hits = DDGS().news(query, max_results=6)
    except Exception as e:
        return f"News search failed: {e}"
    return "\n".join(f"[{h.get('title', '')}] {h.get('body', '')} "
                     f"({h.get('source', '')}, {h.get('date', '')})" for h in hits) or "No news found."


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


@tool
def remember(fact: str) -> str:
    """Remember a fact about the user for future conversations. Use ONLY when the user asks you to
    remember something (for example 'remember that my sister's birthday is 3 May')."""
    DATA_DIR.mkdir(exist_ok=True)
    with FACTS.open("a", encoding="utf-8") as f:
        f.write(fact.strip().replace("\n", " ")[:300] + "\n")
    return "Remembered."
