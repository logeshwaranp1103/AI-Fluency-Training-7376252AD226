"""Ask the LLM the questions directly, with no tool access."""
from config import client, MODEL, QUESTIONS, banner

SYSTEM_PROMPT = (
    "You are a helpful college assistant. Answer the user's question directly from "
    "your own trained knowledge. You do not have access to files, websites, or tools. "
    "Do not pretend that you looked up private college information. If you do not know "
    "a private fact, say that you do not have access to that information."
)


def ask_without_tool(question: str) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ],
        temperature=0,
    )
    return (response.choices[0].message.content or "").strip()


if __name__ == "__main__":
    banner("PLAIN LLM - NO TOOL")
    for number, question in enumerate(QUESTIONS, 1):
        print(f"Q{number}: {question}")
        print(f"A{number}: {ask_without_tool(question)}\n")
