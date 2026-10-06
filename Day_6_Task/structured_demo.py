"""Day 6: compare free text, JSON mode and strict schema mode."""

import json

from config import client, MODEL, banner

SCHEMA = {
    "type": "object",
    "properties": {
        "category": {
            "type": "string",
            "enum": ["Food", "Transport", "Entertainment", "Education"],
        },
        "needs_budget_lookup": {"type": "boolean"},
        "needs_spending_lookup": {"type": "boolean"},
    },
    "required": ["category", "needs_budget_lookup", "needs_spending_lookup"],
    "additionalProperties": False,
}

QUESTION = (
    "I spent money on food and want to know whether I am over my food budget."
)

def ask(response_format, label):
    print(f"\n--- {label} ---")
    try:
        reply = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Extract the request as JSON with keys category, "
                        "needs_budget_lookup and needs_spending_lookup. "
                        "Reply with JSON only."
                    ),
                },
                {"role": "user", "content": QUESTION},
            ],
            temperature=0,
            response_format=response_format,
        )

        text = (reply.choices[0].message.content or "").strip()
        print("raw    :", text)
        try:
            print("parsed :", json.loads(text))
        except json.JSONDecodeError as error:
            print("parsed : ERROR -", error)

    except Exception as error:
        print(f"not supported here ({type(error).__name__}: {error})")

if __name__ == "__main__":
    banner("STRUCTURED OUTPUTS")

    ask(None, "1. No constraint (free text)")
    ask({"type": "json_object"}, "2. JSON mode")
    ask(
        {
            "type": "json_schema",
            "json_schema": {
                "name": "expense_query",
                "schema": SCHEMA,
                "strict": True,
            },
        },
        "3. Schema mode (strict)",
    )
