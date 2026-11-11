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
2. Get a **free** API key at <https://console.groq.com/keys> (no card needed). Prefer Google? Use a free
   Gemini key from <https://aistudio.google.com/apikey>. See "Choosing a brain" below.
3. In a terminal:

```bash
git clone https://github.com/YOUR-USERNAME/vega.git
cd vega
python -m venv .venv
.venv\Scripts\activate            # Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env            # Mac/Linux: cp .env.example .env
```

4. Open `.env` and paste your key after `GROQ_API_KEY=`.
5. Run it:

```bash
python -m vega            # web HUD (opens in your browser; use Chrome or Edge for the mic)
python -m vega text       # plain terminal chat
python -m vega voice      # voice in the terminal (see "Terminal voice")
python -m vega voice --wake   # only reacts after you say "hey vega"
```

## Choosing a brain

Set `VEGA_PROVIDER` in `.env`:

| Provider | Cost | Key variable | Notes |
|---|---|---|---|
| `groq` (default) | Free tier | `GROQ_API_KEY` | Fast. Free limits are per day, so heavy use may pause until tomorrow. |
| `gemini` | Free tier | `GEMINI_API_KEY` | If it errors about the model name, set `VEGA_MODEL` to a current free Gemini model. |
| `ollama` | Free, offline | none | Install Ollama, run `ollama pull llama3.1`, then set `VEGA_PROVIDER=ollama`. Needs a decent PC. |
| `anthropic` | Paid | `ANTHROPIC_API_KEY` | Claude. Needs prepaid credits. |

Free tiers and model names change often. If a model is retired, pick another with `VEGA_MODEL`.
The `stages/` scripts use the Anthropic API and are for learning only.

## Hands-free and Jarvis mode

Click **Hands-free** in the HUD (Chrome or Edge) and say "Hey Vega, ..." any time. Set `VEGA_USER=YourName`
in `.env` so Vega addresses you by name. Extra PC tools: volume, media keys (play/pause/next) and screenshots
(saved to Pictures). Windows only for volume and media.

## Speak in your own voice (optional, free, local)

1. Record 10 to 30 seconds of clean speech (no music or background noise) and save it as `voice/me.wav`.
2. `pip install -r requirements-clone.txt` (big download). On first use it asks you to accept the XTTS
   license in the terminal, then downloads the model.
3. Restart Vega. If `voice/me.wav` exists, Vega speaks with your voice; otherwise it uses the browser voice.

It runs on your CPU or GPU, so on a CPU each reply can take several seconds. Your recording never leaves
your PC and is git-ignored. Only clone your own voice, or one you have permission to use.

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
