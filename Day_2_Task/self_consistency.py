"""Day 2: Self-consistency experiment on a library planning question."""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Day_1')))

from collections import Counter
from config import client, MODEL, banner
from cot_compare import COT_PROMPT

RUNS = 5
TEMPERATURE = 0.8

QUESTION = (
    "A library has 48 seats. 3/8 of the seats are occupied by first-year students "
    "and 1/4 are occupied by second-year students. How many seats are occupied?"
)

def final_answer(text):
    """Extract the final answer from a CoT response."""
    for line in reversed(text.splitlines()):
        if "final answer" in line.lower():
            return line.split(":", 1)[-1].strip()
    return text.splitlines()[-1].strip() if text.strip() else "(empty)"

def run_many(question, runs=RUNS, temperature=TEMPERATURE):
    answers = []

    for attempt in range(1, runs + 1):
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": COT_PROMPT},
                {"role": "user", "content": question}
            ],
            temperature=temperature
        )

        answer = final_answer(response.choices[0].message.content)
        print(f"   run {attempt}: {answer}")
        answers.append(answer)

    return answers

if __name__ == "__main__":
    banner("SELF-CONSISTENCY - LIBRARY SEAT QUESTION")
    print("QUESTION:", QUESTION, "\n")

    answers = run_many(QUESTION)

    winner, count = Counter(answers).most_common(1)[0]

    print(f"\nMajority answer ({count} of {len(answers)} runs): {winner}")
    print("\nExpected correct answer: 30 seats")
    print("At temperature 0, repeated runs should normally be much more consistent.")
