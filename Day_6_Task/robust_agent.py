"""Day 6: robust student expense agent with validation and retry."""

import json

from config import client, MODEL, banner
from tools_v2 import TOOLS, TOOL_FUNCTIONS, SCHEMAS
from validate import validate_arguments

SYSTEM_PROMPT = (
    "You are a student expense and budget assistant. "
    "Never invent spending or budget values. Use get_spending and get_budget "
    "for stored data. Use calculator for every arithmetic step. "
    "Valid categories are Food, Transport, Entertainment, Education. "
    "If no tool is needed, answer directly. Keep final answers concise."
)

MAX_TOKENS = 500
REPEAT_LIMIT = 3

def handle_tool_call(call, log=True):
    """Parse, look up, validate and execute one tool call safely."""
    name = call.function.name
    raw = call.function.arguments or "{}"

    # 1. Parse generated text as JSON.
    try:
        arguments = json.loads(raw)
    except json.JSONDecodeError as error:
        return f"Argument error: invalid JSON ({error}). Send valid JSON for '{name}'."

    # 2. Check that the requested tool exists.
    function = TOOL_FUNCTIONS.get(name)
    if function is None:
        return f"Unknown tool: {name}. Available tools: {', '.join(TOOL_FUNCTIONS)}."

    # 3. Validate the arguments before executing the function.
    problem = validate_arguments(arguments, SCHEMAS[name])
    if problem:
        return f"Argument error: {problem}"

    # 4. Execute the function defensively.
    try:
        result = str(function(**arguments))
    except Exception as error:
        result = f"Tool error in {name}: {type(error).__name__}: {error}"

    if log:
        print(f"  {name}({arguments}) -> {result[:120]}")
    return result

def agent(question, max_steps=6, verbose=True):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]

    seen = {}
    max_tokens = MAX_TOKENS

    for step in range(1, max_steps + 1):
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            temperature=0,
            max_tokens=max_tokens,
        )

        choice = response.choices[0]
        message = choice.message

        # A length finish means the reply was truncated.
        if choice.finish_reason == "length":
            if max_tokens >= 2000:
                return "Stopped: the reply was still truncated at 2000 tokens."
            max_tokens *= 2
            if verbose:
                print(f"  step {step}: truncated, retrying with max_tokens={max_tokens}")
            continue

        # No tool call means this is the final answer.
        if not message.tool_calls:
            return (message.content or "").strip()

        # Preserve every tool call in the assistant message.
        messages.append({
            "role": "assistant",
            "content": message.content or "",
            "tool_calls": [
                {
                    "id": call.id,
                    "type": "function",
                    "function": {
                        "name": call.function.name,
                        "arguments": call.function.arguments,
                    },
                }
                for call in message.tool_calls
            ],
        })

        if verbose:
            print(f"  step {step}: {len(message.tool_calls)} tool call(s)")

        # Every tool call gets exactly one tool message.
        for call in message.tool_calls:
            signature = (call.function.name, call.function.arguments)
            seen[signature] = seen.get(signature, 0) + 1

            if seen[signature] >= REPEAT_LIMIT:
                return (
                    f"Stopped: {call.function.name} was called "
                    f"{REPEAT_LIMIT} times with the same arguments and made no progress."
                )

            result = handle_tool_call(call, log=verbose)
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": result,
            })

    return "Stopped: maximum steps reached without a final answer."

if __name__ == "__main__":
    banner("ROBUST STUDENT EXPENSE AGENT")

    questions = [
        "How much did I spend on Food?",
        "Compare my Food spending with the Food budget and tell me the difference.",
        "Compare my Food spending and budget, and also compare my Transport spending and budget.",
        "Should I reduce my shopping spending?",
        "Give me one short budgeting tip for a student.",
    ]

    for question in questions:
        print("\nQ:", question)
        try:
            print("A:", agent(question))
        except Exception as error:
            print("A: Agent request failed:", type(error).__name__, error)
