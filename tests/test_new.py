from datetime import datetime
from types import SimpleNamespace as NS

from vega import config, tools
from vega.text import detect_lang, split_reply, speakable
from vega.tools import google


def test_prompt_has_todays_date_and_search_rules():
    p = config.build_system(datetime(2026, 11, 11, 9, 30))
    assert "11 November 2026" in p and "web_search" in p and "ONLY when the user" in p


def test_short_reply_is_spoken_as_is():
    shown, spoken = split_reply("It is half past nine, sir.")
    assert shown == spoken == "It is half past nine, sir."


def test_long_draft_is_shown_but_briefly_spoken():
    draft = "Subject: Leave request\n\nDear Sir,\n\nI need leave.\n\n---\n\nRegards,\nKusuma"
    shown, spoken = split_reply(draft)
    assert "Dear Sir" in shown and "---" not in shown
    assert spoken == "I've put that on screen."


def test_screen_line_follows_language():
    assert detect_lang("ನಮಸ್ಕಾರ ಹೇಗಿದ್ದೀರಿ") == "kn" and detect_lang("hello") == "en"
    assert split_reply("ನಮಸ್ಕಾರ\n" * 6)[1] != "I've put that on screen."


def test_links_are_not_read_aloud():
    assert "http" not in speakable("See https://example.com/a?b=1 for more")


def test_open_website_description_discourages_overuse():
    assert "ONLY" in tools.registry.TOOLS["open_website"]["schema"]["description"]


def test_google_tools_hidden_until_signed_in():
    assert config.google_connected() == ("list_unread_emails" in tools.registry.TOOLS)


def test_gmail_body_parsing():
    import base64
    enc = lambda s: base64.urlsafe_b64encode(s.encode()).decode().rstrip("=")
    payload = {"mimeType": "multipart/alternative", "parts": [
        {"mimeType": "text/html", "body": {"data": enc("<p>Hi <b>there</b></p>")}},
        {"mimeType": "text/plain", "body": {"data": enc("Hi there, plain")}}]}
    assert google._body_text(payload) == "Hi there, plain"
    assert google._body_text({"mimeType": "text/html", "body": {"data": enc("<style>x{}</style><p>Hello</p>")}}) == "Hello"


def test_remember_goes_into_the_prompt(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "FACTS", tmp_path / "facts.txt")
    from vega.tools import basics
    monkeypatch.setattr(basics, "FACTS", tmp_path / "facts.txt")
    monkeypatch.setattr(basics, "DATA_DIR", tmp_path)
    assert tools.run("remember", {"fact": "my sister is Asha"}) == "Remembered."
    assert "my sister is Asha" in config.build_system()


def test_openai_brain_refreshes_system_prompt():
    from vega.brain import OpenAIBrain
    create = lambda **kw: NS(choices=[NS(message=NS(tool_calls=None, content="ok"))])
    b = OpenAIBrain(client=NS(chat=NS(completions=NS(create=create))))
    b.messages[0]["content"] = "stale"
    b.ask("hi")
    assert b.messages[0]["content"] != "stale"
