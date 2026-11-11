"""Ears and mouth for terminal mode. Needs: pip install -r requirements-voice.txt"""


def speak(text: str):
    import pyttsx3
    engine = pyttsx3.init()  # fresh engine each time avoids a known hang on Windows
    engine.say(text)
    engine.runAndWait()


def listen(timeout: int = 8) -> str:
    import speech_recognition as sr
    rec = sr.Recognizer()
    with sr.Microphone() as mic:
        rec.adjust_for_ambient_noise(mic, duration=0.4)
        try:
            audio = rec.listen(mic, timeout=timeout, phrase_time_limit=15)
            return rec.recognize_google(audio)
        except (sr.WaitTimeoutError, sr.UnknownValueError):
            return ""
