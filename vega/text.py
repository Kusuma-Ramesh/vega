"""Turn a model reply into (what to show on screen, what to say aloud)."""
import re

_URL = re.compile(r"https?://\S+")
_SEPARATOR = re.compile(r"^\s*(?:-{3,}|_{3,}|\*{3,}|={3,})\s*$", re.M)
# (unicode range, language code)
_SCRIPTS = [
    ("\u0c80-\u0cff", "kn"), ("\u0c00-\u0c7f", "te"), ("\u0900-\u097f", "hi"),
    ("\u0b80-\u0bff", "ta"), ("\u0d00-\u0d7f", "ml"), ("\u0980-\u09ff", "bn"),
    ("\u0a80-\u0aff", "gu"), ("\u0a00-\u0a7f", "pa"), ("\u0600-\u06ff", "ur"),
]
SCREEN_LINE = {
    "en": "I've put that on screen.",
    "hi": "मैंने इसे स्क्रीन पर रख दिया है।",
    "kn": "ನಾನು ಅದನ್ನು ಪರದೆಯ ಮೇಲೆ ಇಟ್ಟಿದ್ದೇನೆ.",
    "te": "నేను దానిని స్క్రీన్‌పై ఉంచాను.",
}


def detect_lang(text: str) -> str:
    """Rough language code from the script the text is written in ('en' if Latin)."""
    best, most = "en", 0
    for rng, code in _SCRIPTS:
        n = len(re.findall(f"[{rng}]", text))
        if n > most:
            best, most = code, n
    return best


def tidy(text: str) -> str:
    """Light clean-up for showing on screen: drop markdown noise and '---' lines."""
    t = text.replace("\r", "")
    t = _SEPARATOR.sub("", t)
    t = re.sub(r"\*\*|__|`+", "", t)
    t = re.sub(r"^\s*#{1,6}\s*", "", t, flags=re.M)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def speakable(text: str) -> str:
    """Plain text that sounds fine when read aloud: no markdown, no links."""
    t = _URL.sub("link", tidy(text))
    t = re.sub(r"[*_`#>]+", "", t)
    t = re.sub(r"\s*\n+\s*", ". ", t)
    return re.sub(r"\s{2,}", " ", t).strip()


def is_long(text: str) -> bool:
    t = text.strip()
    return len(t) > 420 or t.count("\n") >= 4 or bool(_SEPARATOR.search(t))


def split_reply(text: str):
    """Return (display, spoken). Long drafts are shown in full but only briefly spoken."""
    display = tidy(text)
    if is_long(text):
        return display, SCREEN_LINE.get(detect_lang(text), SCREEN_LINE["en"])
    return display, speakable(text)
