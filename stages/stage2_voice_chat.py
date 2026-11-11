"""STAGE 2 - Add ears and a mouth. Needs: pip install -r requirements-voice.txt"""
import anthropic
import pyttsx3
import speech_recognition as sr
from dotenv import load_dotenv

load_dotenv()
client, history, rec = anthropic.Anthropic(), [], sr.Recognizer()


def listen():
    with sr.Microphone() as mic:
        rec.adjust_for_ambient_noise(mic, duration=0.4)
        try:
            return rec.recognize_google(rec.listen(mic, timeout=8, phrase_time_limit=15))
        except (sr.WaitTimeoutError, sr.UnknownValueError):
            return ""


def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


while True:
    user = listen()
    if not user:
        continue
    print("you >", user)
    if "goodbye" in user.lower():
        break
    history.append({"role": "user", "content": user})
    reply = client.messages.create(
        model="claude-sonnet-5-5", max_tokens=400,
        system="You are Vega. Replies are spoken aloud: short, no markdown.",
        messages=history,
    ).content[0].text
    history.append({"role": "assistant", "content": reply})
    print("vega >", reply)
    speak(reply)
