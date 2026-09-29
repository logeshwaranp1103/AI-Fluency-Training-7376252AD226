"""Ask the same questions with exactly one tool available to the LLM."""
import json
from config import client, MODEL, QUESTIONS, banner
from my_tools import TOOLS, TOOL_FUNCTIONS

SYSTEM_PROMPT = (
    "You are a college assistant. You have one tool called read_event_info. "
    "The tool contains private/local information about the AI Workshop. "
    "If the user asks for a factual detail about that workshop, use the tool before "
    "answering. Do not invent event facts. If the question can be answered without "
    "the private event file, answer directly and do not call the tool. "
    "After receiving a tool result, use that result in your final answer."
)


def ask_with_tool(question: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
        temperature=0,
    )
    message = response.choices[0].message

    if not message.tool_calls:
        print("Tool call: NONE")
        return (message.content or "").strip()

    # The assignment asks us to demonstrate one working tool call, not a full loop.
    call = message.tool_calls[0]
    name = call.function.name
    raw_arguments = call.function.arguments or "{}"
    try:
        arguments = json.loads(raw_arguments)
    except json.JSONDecodeError:
        arguments = {}

    # Some OpenAI-compatible providers/models return an empty-key object
    # for a function that intentionally has no parameters, e.g. {"": {}}.
    # Our tool takes no arguments, so normalize that representation to {}.
    if not isinstance(arguments, dict) or (len(arguments) == 1 and "" in arguments):
        arguments = {}

    print(f"Tool call: {name}({arguments})")

    function = TOOL_FUNCTIONS.get(name)
    if function is None:
        result = f"Tool error: unknown tool '{name}'."
    else:
        result = str(function(**arguments))

    messages.append({
        "role": "assistant",
        "content": message.content or "",
        "tool_calls": [{
            "id": call.id,
            "type": "function",
            "function": {
                "name": name,
                "arguments": call.function.arguments,
            },
        }],
    })
    messages.append({
        "role": "tool",
        "tool_call_id": call.id,
        "content": result,
    })

    final_response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0,
    )
    return (final_response.choices[0].message.content or "").strip()


if __name__ == "__main__":
    banner("LLM + ONE TOOL")
    for number, question in enumerate(QUESTIONS, 1):
        print(f"Q{number}: {question}")
        print(f"A{number}: {ask_with_tool(question)}\n")
