"""STAGE 1 - A text brain. Run: python stages/stage1_text_chat.py"""
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()          # reads ANTHROPIC_API_KEY from .env
history = []                            # the assistant's memory

while True:
    user = input("you > ")
    if user.lower() in ("quit", "exit"):
        break
    history.append({"role": "user", "content": user})
    reply = client.messages.create(
        model="claude-sonnet-5-5", max_tokens=500,
        system="You are Vega, a witty assistant. Keep answers short.",
        messages=history,
    )
    text = reply.content[0].text
    history.append({"role": "assistant", "content": text})
    print("vega >", text)
