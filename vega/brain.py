"""The brain: Claude plus a tool-use loop."""
import anthropic

from . import tools
from .config import MODEL, SYSTEM


class Brain:
    def __init__(self, on_event=None, client=None):
        self.client = client or anthropic.Anthropic()  # reads ANTHROPIC_API_KEY
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
