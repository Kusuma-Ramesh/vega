"""PC-control tools. Deliberately limited: an app allowlist, http(s) links only,
and file search confined to your home folder. Nothing here deletes or edits files."""
import os
import platform
import subprocess
import threading
import webbrowser
from datetime import datetime
from pathlib import Path

from .registry import state, tool

OS = platform.system()  # "Windows", "Darwin" or "Linux"
# Add your own apps here. Only names in this list can ever be launched.
APPS = {
    "notepad": {"Windows": ["notepad"]},
    "calculator": {"Windows": ["calc"], "Darwin": ["open", "-a", "Calculator"], "Linux": ["gnome-calculator"]},
    "chrome": {"Windows": ["cmd", "/c", "start", "", "chrome"], "Darwin": ["open", "-a", "Google Chrome"], "Linux": ["google-chrome"]},
    "vscode": {"Windows": ["cmd", "/c", "start", "", "code"], "Darwin": ["open", "-a", "Visual Studio Code"], "Linux": ["code"]},
    "files": {"Windows": ["explorer"], "Darwin": ["open", "."], "Linux": ["xdg-open", "."]},
    "edge": {"Windows": ["cmd", "/c", "start", "", "msedge"]},
    "paint": {"Windows": ["mspaint"]},
    "settings": {"Windows": ["cmd", "/c", "start", "", "ms-settings:"]},
    "task manager": {"Windows": ["taskmgr"]},
}


@tool
def open_app(name: str) -> str:
    """Open an allowed desktop app. Allowed: notepad, calculator, chrome, edge, vscode, files, paint, settings, task manager."""
    cmd = APPS.get(name.lower().strip(), {}).get(OS)
    if not cmd:
        return f"I'm not allowed to open '{name}'. Allowed: {', '.join(APPS)}."
    subprocess.Popen(cmd)
    return f"Opened {name}."


@tool
def open_website(url: str) -> str:
    """Open a web page in the default browser. ONLY use this when the user explicitly asks to open or go to
    a site. Never use it to answer questions or read news; use web_search or news_search for that."""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    webbrowser.open(url)
    return f"Opened {url}."


@tool
def find_files(name: str, folder: str = "Documents") -> str:
    """Find files whose name contains the text, inside a folder under the user's home (e.g. Documents, Downloads, Desktop)."""
    home = Path.home().resolve()
    root = (home / folder).resolve()
    if home not in root.parents and root != home:
        return "I can only search inside your home folder."
    found, scanned = [], 0
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for f in files:
            scanned += 1
            if name.lower() in f.lower():
                found.append(str(Path(dirpath) / f))
        if len(found) >= 10 or scanned > 50000:
            break
    return "\n".join(found[:10]) or "No matching files."


@tool
def set_timer(seconds: int, label: str = "Timer") -> str:
    """Set a timer that alerts the user when it finishes."""
    t = threading.Timer(seconds, lambda: state["notify"](f"{label} is done."))
    t.daemon = True
    t.start()
    return f"Timer set for {seconds} seconds."


@tool
def system_info() -> str:
    """Describe the computer: OS, version and processor."""
    return f"{platform.system()} {platform.release()}, {platform.processor() or platform.machine()}"


def _press(vk, times=1):
    """Tap a Windows media/volume key."""
    if OS != "Windows":
        return False
    import ctypes
    for _ in range(times):
        ctypes.windll.user32.keybd_event(vk, 0, 0, 0)
        ctypes.windll.user32.keybd_event(vk, 0, 2, 0)
    return True


@tool
def volume(action: str, steps: int = 5) -> str:
    """Change the system volume. action is up, down or mute. Each step is about 2 percent."""
    vk = {"up": 0xAF, "down": 0xAE, "mute": 0xAD}.get(action)
    if not vk:
        return "action must be up, down or mute."
    return "Done." if _press(vk, 1 if action == "mute" else steps) else "Volume control works on Windows only."


@tool
def media(action: str) -> str:
    """Control music or video playback. action is play_pause, next or previous."""
    vk = {"play_pause": 0xB3, "next": 0xB0, "previous": 0xB1}.get(action)
    if not vk:
        return "action must be play_pause, next or previous."
    return "Done." if _press(vk) else "Media keys work on Windows only."


@tool
def screenshot() -> str:
    """Take a screenshot of the screen and save it in the Pictures folder."""
    from PIL import ImageGrab
    path = Path.home() / "Pictures" / f"vega-{datetime.now():%Y%m%d-%H%M%S}.png"
    path.parent.mkdir(exist_ok=True)
    ImageGrab.grab().save(path)
    return f"Saved to {path}"
