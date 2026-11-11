from types import SimpleNamespace as NS

from vega import tools
from vega.brain import Brain


def test_schema_from_type_hints():
    s = tools.registry.TOOLS["set_timer"]["schema"]["input_schema"]
    assert s["properties"]["seconds"]["type"] == "integer" and s["required"] == ["seconds"]


def test_open_app_allowlist():
    assert "not allowed" in tools.run("open_app", {"name": "rm -rf /"})


def test_find_files_stays_in_home():
    assert "home folder" in tools.run("find_files", {"name": "x", "folder": "../../etc"})


def test_brain_tool_loop():
    calls = iter([
        NS(stop_reason="tool_use", content=[NS(type="tool_use", id="1", name="get_time", input={})]),
        NS(stop_reason="end_turn", content=[NS(type="text", text="It is time.")]),
    ])
    client = NS(messages=NS(create=lambda **kw: next(calls)))
    assert Brain(client=client).ask("time?") == "It is time."


def test_openai_brain_tool_loop():
    from vega.brain import OpenAIBrain
    call = NS(id="c1", function=NS(name="get_time", arguments="{}"))
    replies = iter([NS(tool_calls=[call], content=None), NS(tool_calls=None, content="Noon.")])
    create = lambda **kw: NS(choices=[NS(message=next(replies))])
    client = NS(chat=NS(completions=NS(create=create)))
    b = OpenAIBrain(client=client)
    assert b.ask("time?") == "Noon."
    assert [m["role"] for m in b.messages] == ["system", "user", "assistant", "tool", "assistant"]
