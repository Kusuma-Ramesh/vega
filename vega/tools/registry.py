"""Tiny tool registry: decorate a function with @tool and Claude can call it.
The schema is built from the function's type hints and docstring."""
import inspect

TOOLS = {}
state = {"notify": print}  # the CLI/web UI swaps this to show timer alerts
_TYPES = {str: "string", int: "integer", float: "number", bool: "boolean"}


def tool(fn):
    props, required = {}, []
    for name, p in inspect.signature(fn).parameters.items():
        props[name] = {"type": _TYPES.get(p.annotation, "string")}
        if p.default is inspect.Parameter.empty:
            required.append(name)
    TOOLS[fn.__name__] = {
        "fn": fn,
        "schema": {
            "name": fn.__name__,
            "description": inspect.getdoc(fn) or fn.__name__,
            "input_schema": {"type": "object", "properties": props, "required": required},
        },
    }
    return fn


def schemas():
    return [t["schema"] for t in TOOLS.values()]


def run(name, args):
    if name not in TOOLS:
        return f"Unknown tool: {name}"
    try:
        return str(TOOLS[name]["fn"](**args))[:6000]  # keep one tool result from flooding the model
    except Exception as e:  # tell Claude what broke instead of crashing
        return f"Tool error: {e}"
