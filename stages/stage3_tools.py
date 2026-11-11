"""STAGE 3 - Give Claude a tool. Claude decides WHEN to call it; your code does the work."""
from datetime import datetime

import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()
TOOLS = [{
    "name": "get_time",
    "description": "Get the current local date and time.",
    "input_schema": {"type": "object", "properties": {}},
}]
history = []

while True:
    history.append({"role": "user", "content": input("you > ")})
    while True:  # keep going until Claude has a final answer
        resp = client.messages.create(model="claude-sonnet-5-5", max_tokens=400,
                                      tools=TOOLS, messages=history)
        history.append({"role": "assistant", "content": resp.content})
        if resp.stop_reason != "tool_use":
            break
        results = []
        for block in resp.content:
            if block.type == "tool_use":
                print(f"  (using tool: {block.name})")
                results.append({"type": "tool_result", "tool_use_id": block.id,
                                "content": datetime.now().strftime("%A %d %B %Y, %I:%M %p")})
        history.append({"role": "user", "content": results})
    print("vega >", "".join(b.text for b in resp.content if b.type == "text"))
