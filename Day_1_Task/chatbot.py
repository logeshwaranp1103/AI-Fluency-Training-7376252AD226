import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """
You are a plain chatbot for a private personal library management system.

You do NOT have access to the user's private book collection,
reading-goal files, or other private data.

If the user asks about their actual books or reading goals,
explain that you cannot access their private data.

Do not invent private library information.
"""


def chatbot(user_message):
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        temperature=0.2
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    question = (
        "Analyze my private book collection and tell me "
        "which reading categories have reached their goals."
    )

    print()
    print("=" * 72)
    print("                         PLAIN CHATBOT")
    print("=" * 72)

    print("\n[1] USER REQUEST")
    print("-" * 72)
    print(question)

    print("\n[2] PROCESS")
    print("-" * 72)
    print("LLM receives the request.")
    print("No private-data tools are available.")
    print("The chatbot cannot access book or reading-goal files.")

    answer = chatbot(question)

    print("\n[3] CHATBOT RESPONSE")
    print("-" * 72)
    print(answer)

    print("\n[4] CAPABILITIES")
    print("-" * 72)
    print("Private data access : NO")
    print("Tool usage          : NONE")
    print("Decision mechanism  : LLM response")
    print("Multi-step actions  : NO")

    print("\n" + "=" * 72)
