"""Day 2: Direct Prompting vs Chain-of-Thought on a Library Planning Scenario."""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Day_1')))

from config import client, MODEL, banner

# Own scenario: planning a student's library study session.
QUESTIONS = [
    "A student plans to study in the library for 5 hours. "
    "She spends 1 hour on DSA, 1 hour 30 minutes on Python, and 45 minutes on DBMS. "
    "How much study time is left?",

    "A library has 48 seats. 3/8 of the seats are occupied by first-year students "
    "and 1/4 are occupied by second-year students. How many seats are occupied?",

    "A student enters the library before Arun. Arun enters before Bala. "
    "Bala enters before Charan. Who entered first and who entered last?"
]

DIRECT_PROMPT = (
    "You are a helpful assistant. Answer the question directly. "
    "Give only the final answer without showing your reasoning."
)

COT_PROMPT = (
    "You are a helpful assistant. Solve the problem step by step. "
    "Number each step and show the calculation. "
    "After the steps, write the last line exactly as: Final Answer: <answer>"
)

def ask(system_prompt, question):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ],
        temperature=0
    )
    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    banner("LIBRARY STUDY PLANNING - DIRECT vs CoT")

    for number, question in enumerate(QUESTIONS, start=1):
        print("=" * 72)
        print(f"QUESTION {number}: {question}\n")

        print("--- DIRECT PROMPTING ---")
        print(ask(DIRECT_PROMPT, question), "\n")

        print("--- CHAIN-OF-THOUGHT ---")
        print(ask(COT_PROMPT, question), "\n")
