# VEGA

**V**oice-**E**nabled **G**enius **A**ssistant: a personal assistant for your PC, powered by Claude.
Talk or type to it, and it can search the web, check the weather, take notes, set timers,
open apps and find files, behind a glowing star interface in your browser.

```
 browser (face + ears + mouth)  <--websocket-->  Python (brain)  --->  Claude API
  HUD, mic, speech synthesis                      tool loop + your PC tools
```

## Quick start (Windows, Mac or Linux)

1. Install **Python 3.10+** from python.org (on Windows, tick *Add Python to PATH*).
2. Get an API key at <https://console.anthropic.com> (billed by usage, separate from a Claude chat plan).
3. In a terminal:

```bash
git clone https://github.com/YOUR-USERNAME/vega.git
cd vega
python -m venv .venv
.venv\Scripts\activate            # Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env            # Mac/Linux: cp .env.example .env
```

4. Open `.env` and paste your key after `ANTHROPIC_API_KEY=`.
5. Run it:

```bash
python -m vega            # web HUD (opens in your browser; use Chrome or Edge for the mic)
python -m vega text       # plain terminal chat
python -m vega voice      # voice in the terminal (see "Terminal voice")
python -m vega voice --wake   # only reacts after you say "hey vega"
```

## Built in five stages (learn by reading)

| Stage | What it adds | Where |
|---|---|---|
| 1 | A text brain with memory | `stages/stage1_text_chat.py` |
| 2 | Ears and a mouth | `stages/stage2_voice_chat.py` |
| 3 | Tools Claude can call | `stages/stage3_tools.py` |
| 4 | PC control, kept safe | `vega/tools/system.py` |
| 5 | The HUD in your browser | `web/index.html`, `vega/server.py` |

Run the stage files one by one to see each idea on its own. The real app (`vega/`) is those
same ideas, tidied up. Start with `vega/brain.py`; it's about 40 lines.

## Add your own tool

Write a function in `vega/tools/basics.py` (or a new file imported in `vega/tools/__init__.py`).
The `@tool` decorator and the docstring are all Claude needs:

```python
@tool
def coin_flip() -> str:
    """Flip a coin."""
    import random
    return random.choice(["Heads", "Tails"])
```

Restart Vega and say "flip a coin". Type hints (`str`, `int`, `float`, `bool`) become the argument types.

## Terminal voice

`pip install -r requirements-voice.txt`. If `PyAudio` fails on Windows, update pip and use a
supported Python version (3.10 to 3.12 are safest). The web HUD needs none of this, because the
browser handles speech.

## Safety

- The server listens on `127.0.0.1` only and rejects WebSocket connections from other sites.
- `open_app` launches only apps in the `APPS` allowlist. `open_website` allows http(s) links only.
- `find_files` searches inside your home folder and never edits or deletes anything.
- There is deliberately **no shell or delete tool**. If you add one, require a yes/no confirmation first.
- Notes live in `~/.vega/notes.txt`. Never commit your `.env`.

## Ideas for what's next

Calendar and email tools, a custom wake word, music control, a smarter memory (save facts between runs),
and swapping the browser voice for a neural voice.

## Tests

```bash
pip install pytest
python -m pytest
```

MIT licensed.
