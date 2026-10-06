"""Day 6: deliberately inject broken tool calls without using a model."""

import json

from robust_agent import handle_tool_call

class FakeFunction:
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

class FakeCall:
    def __init__(self, name, arguments, call_id="call_test"):
        self.id = call_id
        self.type = "function"
        self.function = FakeFunction(name, arguments)

FAULTS = [
    ("good call", FakeCall("get_spending", '{"category": "Food"}')),
    ("invalid JSON", FakeCall("get_spending", '{"category": "Food"')),
    ("unknown tool", FakeCall("send_email", '{"to": "student@example.com"}')),
    ("missing required", FakeCall("get_spending", '{}')),
    ("wrong type", FakeCall("get_spending", '{"category": 101}')),
    ("value outside enum", FakeCall("get_spending", '{"category": "Shopping"}')),
    ("invented extra argument",
     FakeCall("get_spending", '{"category": "Food", "month": "September"}')),
    # Own fault 1: JSON is valid, but the top-level shape is an array.
    ("own fault - JSON array",
     FakeCall("get_spending", json.dumps(["Food"]))),
    # Own fault 2: valid schema arguments, but unsafe calculator input.
    ("own fault - unsafe expression",
     FakeCall("calculator", json.dumps({"expression": "__import__('os').system('dir')"}))),
]

if __name__ == "__main__":
    print("=" * 90)
    print("FAULT INJECTION - no model and no internet required")
    print("=" * 90)

    for label, call in FAULTS:
        result = handle_tool_call(call, log=False)
        print(f"{label:<30} -> {result}")

    print("=" * 90)
    print("Every result above is a string. The handler does not crash on these faults.")
