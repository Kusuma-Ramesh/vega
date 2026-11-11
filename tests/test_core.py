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
