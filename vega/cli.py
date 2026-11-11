import argparse
import threading
import webbrowser

from .config import NAME, PORT

EXIT = {"quit", "exit", "goodbye", "stop"}


def run_text(brain, voice=False, wake=False):
    wake_phrase = f"hey {NAME.lower()}"
    if voice:
        from . import voice as v
    print(f"{NAME} online. {'Speak' if voice else 'Type'} to talk; say or type 'goodbye' to quit.")
    while True:
        try:
            text = v.listen() if voice else input("you > ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not text:
            continue
        if voice:
            print("you >", text)
            if wake:
                if wake_phrase not in text.lower():
                    continue
                text = text.lower().split(wake_phrase, 1)[1].strip() or "hello"
        if text.lower().strip(" .!") in EXIT:
            break
        try:
            reply = brain.ask(text)
        except Exception as e:
            reply = f"Something went wrong: {e}"
        print(f"{NAME} >", reply)
        if voice:
            v.speak(reply)


def main():
    p = argparse.ArgumentParser(prog="vega", description="VEGA assistant")
    p.add_argument("mode", nargs="?", default="web", choices=["text", "voice", "web"])
    p.add_argument("--wake", action="store_true", help="voice mode: only respond after 'hey vega'")
    a = p.parse_args()

    if a.mode == "web":
        import uvicorn
        threading.Timer(1.5, lambda: webbrowser.open(f"http://localhost:{PORT}")).start()
        uvicorn.run("vega.server:app", host="127.0.0.1", port=PORT, log_level="warning")
        return

    from .brain import make_brain
    from .tools import state
    state["notify"] = lambda m: print(f"\n[!] {m}")
    run_text(make_brain(), voice=a.mode == "voice", wake=a.wake)
