import os
import json

from dotenv import load_dotenv
from groq import Groq

from tools import (
    get_books,
    get_reading_goals,
    calculate_category_counts,
    compare_goals
)

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_books",
            "description": "Get the user's private book collection.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_reading_goals",
            "description": "Get the user's private reading goals.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_category_counts",
            "description": "Calculate the number of books in every category.",
            "parameters": {
                "type": "object",
                "properties": {
                    "books": {
                        "type": "array"
                    }
                },
                "required": ["books"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "compare_goals",
            "description": "Compare completed books against reading goals.",
            "parameters": {
                "type": "object",
                "properties": {
                    "books": {
                        "type": "array"
                    },
                    "goals": {
                        "type": "object"
                    }
                },
                "required": ["books", "goals"]
            }
        }
    }
]


def execute_tool(tool_name, arguments):
    if tool_name == "get_books":
        return get_books()

    if tool_name == "get_reading_goals":
        return get_reading_goals()

    if tool_name == "calculate_category_counts":
        return calculate_category_counts(arguments["books"])

    if tool_name == "compare_goals":
        return compare_goals(
            arguments["books"],
            arguments["goals"]
        )

    raise ValueError(f"Unknown tool: {tool_name}")


def display_observation(tool_name, result):
    print("\n    OBSERVATION")
    print("    " + "-" * 56)

    if tool_name == "get_books":
        print(f"    Retrieved {len(result)} private book records.")

    elif tool_name == "get_reading_goals":
        print(f"    Retrieved {len(result)} private reading goals.")

    elif tool_name == "calculate_category_counts":
        print(f"    Calculated totals for {len(result)} categories.")

        for category, count in result.items():
            print(f"    {category:<18}{count:>8}")

    elif tool_name == "compare_goals":
        print(f"    Compared {len(result)} reading goals.")

        for category, data in result.items():
            print(
                f"    {category:<18}"
                f"done={data['completed']}, "
                f"goal={data['goal']}, "
                f"{data['status']}"
            )

    print("    " + "-" * 56)


def run_agent(user_question):
    messages = [
        {
            "role": "system",
            "content": """
You are an AI agent for analyzing a user's private book collection
and reading goals.

Private data is available only through tools.

Your job is to:
1. Understand the user's request.
2. Select the appropriate tool.
3. Execute the tool.
4. Observe the result.
5. Decide whether another tool is required.
6. Continue until enough information is available.
7. Produce a final answer.

Do not invent private library information.
"""
        },
        {
            "role": "user",
            "content": user_question
        }
    ]

    step = 1

    while True:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            temperature=0.1
        )

        assistant_message = response.choices[0].message

        if not assistant_message.tool_calls:
            print("\n" + "=" * 72)
            print("                         FINAL ANSWER")
            print("=" * 72)
            print(assistant_message.content)

            print("\n" + "-" * 72)
            print("[AGENT SUMMARY]")
            print("-" * 72)
            print("Private data access : THROUGH TOOLS")
            print("LLM                 : openai/gpt-oss-20b")
            print("Tool calls          :", step - 1)
            print("Loop status         : COMPLETED")
            print("=" * 72)
            return

        messages.append(assistant_message)

        for tool_call in assistant_message.tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments or "{}")

            print("\n" + "-" * 72)
            print(f"[STEP {step}]")
            print("-" * 72)
            print(f"TOOL SELECTED : {tool_name}")

            if tool_name in ("get_books", "get_reading_goals"):
                print("INPUT         : No arguments")
            elif tool_name == "calculate_category_counts":
                print(
                    "INPUT         : "
                    f"{len(arguments.get('books', []))} book records"
                )
            elif tool_name == "compare_goals":
                print(
                    "INPUT         : "
                    f"{len(arguments.get('books', []))} books and "
                    f"{len(arguments.get('goals', {}))} goals"
                )

            result = execute_tool(tool_name, arguments)

            display_observation(tool_name, result)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })

            step += 1


if __name__ == "__main__":
    question = """
Analyze my private book collection.

Tell me:
1. How many books I have in each category.
2. Which reading goals have been reached.
3. Which reading goals have not been reached.
4. How many more completed books are needed for each unfinished goal.
"""

    print()
    print("=" * 72)
    print("                           AI AGENT")
    print("=" * 72)

    print("\n[USER REQUEST]")
    print("-" * 72)
    print(question)

    print("\n[AGENT EXECUTION]")

    run_agent(question)
