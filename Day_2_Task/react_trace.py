"""Day 2: ReAct agent on a library study-planning scenario.

The agent uses a library-hours tool when it needs external information,
then reasons with the observed result before giving the final answer.
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Day_1_Training')))

from agent import agent

QUESTION = (
    "I want to study in the college library today. "
    "First find out from the library-hours tool when the library closes. "
    "Then calculate whether I can complete a 3-hour study session if I start "
    "at 5:00 PM. If there is not enough time, tell me how much time is missing. "
    "Use the tool result before giving the final answer."
)

if __name__ == "__main__":
    print("SCENARIO: College Library Study Planning\n")
    print("QUESTION:", QUESTION, "\n")
    print("--- ReAct actions and observations ---")

    answer = agent(QUESTION, max_steps=8)

    print("\nFINAL ANSWER:", answer)
