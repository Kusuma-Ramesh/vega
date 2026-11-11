"""The brain: an AI model plus a tool-use loop. Free providers (Groq, Gemini, Ollama) use
the OpenAI-style API; Claude uses the Anthropic API."""

from . import tools
import json

from .config import API_KEY, BASE_URL, MODEL, PROVIDER, SYSTEM


class Brain:
    def __init__(self, on_event=None, client=None):
        import anthropic
        self.client = client or anthropic.Anthropic(api_key=API_KEY)
        self.messages = []
        self.on_event = on_event or (lambda kind, data: None)

    def _trim(self):
        # Keep memory bounded; only cut at a plain user message so tool pairs stay intact.
        while len(self.messages) > 40:
            self.messages.pop(0)
            while self.messages and not (
                self.messages[0]["role"] == "user" and isinstance(self.messages[0]["content"], str)
            ):
                self.messages.pop(0)

    def ask(self, text: str) -> str:
        self.messages.append({"role": "user", "content": text})
        self._trim()
        for _ in range(8):  # safety cap on tool round-trips
            resp = self.client.messages.create(
                model=MODEL, max_tokens=700, system=SYSTEM,
                tools=tools.schemas(), messages=self.messages,
            )
            self.messages.append({"role": "assistant", "content": resp.content})
            if resp.stop_reason != "tool_use":
                return "".join(b.text for b in resp.content if b.type == "text").strip()
            results = []
            for b in resp.content:
                if b.type == "tool_use":
                    self.on_event("tool", {"name": b.name, "args": b.input})
                    out = tools.run(b.name, b.input)
                    results.append({"type": "tool_result", "tool_use_id": b.id, "content": out})
            self.messages.append({"role": "user", "content": results})
        return "I got stuck in a loop on that one. Try rephrasing?"


class OpenAIBrain:
    """Same job as Brain, for any OpenAI-compatible API (Groq, Gemini, Ollama...)."""

    def __init__(self, on_event=None, client=None):
        if client is None:
            from openai import OpenAI
            if not API_KEY:
                raise SystemExit(f"No API key found for '{PROVIDER}'. Add it to your .env file (see .env.example).")
            client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
        self.client = client
        self.messages = [{"role": "system", "content": SYSTEM}]
        self.on_event = on_event or (lambda kind, data: None)

    @staticmethod
    def _tools():
        out = []
        for s in tools.schemas():
            params = dict(s["input_schema"])
            if not params.get("required"):
                params.pop("required", None)
            out.append({"type": "function", "function": {
                "name": s["name"], "description": s["description"], "parameters": params}})
        return out

    def _trim(self):
        while len(self.messages) > 41:
            self.messages.pop(1)  # keep the system prompt at index 0
            while len(self.messages) > 1 and self.messages[1]["role"] != "user":
                self.messages.pop(1)

    def ask(self, text: str) -> str:
        self.messages.append({"role": "user", "content": text})
        self._trim()
        for _ in range(8):
            msg = self.client.chat.completions.create(
                model=MODEL, messages=self.messages, tools=self._tools()).choices[0].message
            calls = msg.tool_calls or []
            entry = {"role": "assistant", "content": msg.content or ""}
            if calls:
                entry["tool_calls"] = [{"id": c.id, "type": "function", "function": {
                    "name": c.function.name, "arguments": c.function.arguments}} for c in calls]
            self.messages.append(entry)
            if not calls:
                return (msg.content or "").strip()
            for c in calls:
                args = json.loads(c.function.arguments or "{}")
                self.on_event("tool", {"name": c.function.name, "args": args})
                self.messages.append({"role": "tool", "tool_call_id": c.id,
                                      "content": tools.run(c.function.name, args)})
        return "I got stuck in a loop on that one. Try rephrasing?"


def make_brain(on_event=None):
    """Pick the right brain for VEGA_PROVIDER."""
    return Brain(on_event) if PROVIDER == "anthropic" else OpenAIBrain(on_event)
