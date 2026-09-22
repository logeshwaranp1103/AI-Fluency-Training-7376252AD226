import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


def load_books():
    with open(DATA_DIR / "books.json", "r", encoding="utf-8") as file:
        return json.load(file)


def load_goals():
    with open(DATA_DIR / "reading_goals.json", "r", encoding="utf-8") as file:
        return json.load(file)


def calculate_category_counts(books):
    counts = {}

    for book in books:
        category = book["category"]
        counts[category] = counts.get(category, 0) + 1

    return counts


def compare_goals(books, goals):
    completed_counts = {}

    for book in books:
        if book["status"] == "Completed":
            category = book["category"]
            completed_counts[category] = completed_counts.get(category, 0) + 1

    results = {}

    for category, goal in goals.items():
        completed = completed_counts.get(category, 0)
        difference = completed - goal

        if difference >= 0:
            status = "GOAL REACHED"
        else:
            status = "GOAL NOT REACHED"

        results[category] = {
            "completed": completed,
            "goal": goal,
            "difference": difference,
            "status": status
        }

    return results


def run_workflow():
    print()
    print("=" * 72)
    print("                      RULE-BASED WORKFLOW")
    print("=" * 72)

    print("\n[STEP 1] LOAD PRIVATE BOOK DATA")
    print("-" * 72)
    books = load_books()
    print(f"Book records loaded    : {len(books)}")

    print("\n[STEP 2] LOAD READING GOALS")
    print("-" * 72)
    goals = load_goals()
    print(f"Goal categories        : {len(goals)}")

    print("\n[STEP 3] CALCULATE CATEGORY COUNTS")
    print("-" * 72)
    counts = calculate_category_counts(books)

    print(f"{'CATEGORY':<20}{'TOTAL BOOKS':>15}")
    print("-" * 35)
    for category, count in counts.items():
        print(f"{category:<20}{count:>15}")

    print("\n[STEP 4] APPLY PREDEFINED GOAL RULES")
    print("-" * 72)
    results = compare_goals(books, goals)

    print("\n" + "=" * 72)
    print("                         FINAL RESULT")
    print("=" * 72)

    print(
        f"{'CATEGORY':<18}"
        f"{'DONE':>10}"
        f"{'GOAL':>10}"
        f"{'DIFFERENCE':>14}"
        f"  STATUS"
    )
    print("-" * 72)

    for category, result in results.items():
        difference = result["difference"]

        if difference >= 0:
            difference_text = f"+{difference}"
        else:
            difference_text = str(difference)

        print(
            f"{category:<18}"
            f"{result['completed']:>10}"
            f"{result['goal']:>10}"
            f"{difference_text:>14}"
            f"  {result['status']}"
        )

    print("-" * 72)

    reached = [
        category
        for category, result in results.items()
        if result["status"] == "GOAL REACHED"
    ]

    not_reached = [
        category
        for category, result in results.items()
        if result["status"] == "GOAL NOT REACHED"
    ]

    print("\n[SUMMARY]")
    print(f"Goals reached     : {', '.join(reached)}")
    print(f"Goals not reached : {', '.join(not_reached)}")

    print("\n[WORKFLOW CHARACTERISTICS]")
    print("-" * 72)
    print("Private data access : YES")
    print("LLM usage           : NO")
    print("Tool selection      : NO")
    print("Decision mechanism  : PREDEFINED RULES")
    print("Execution path      : FIXED")

    print("\n" + "=" * 72)


if __name__ == "__main__":
    run_workflow()
