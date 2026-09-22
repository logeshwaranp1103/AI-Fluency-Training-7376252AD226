import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


def get_books():
    """Return the user's private book collection."""
    with open(DATA_DIR / "books.json", "r", encoding="utf-8") as file:
        return json.load(file)


def get_reading_goals():
    """Return the user's private reading goals by category."""
    with open(DATA_DIR / "reading_goals.json", "r", encoding="utf-8") as file:
        return json.load(file)


def calculate_category_counts(books):
    """Calculate the number of books in each category."""
    counts = {}

    for book in books:
        category = book["category"]
        counts[category] = counts.get(category, 0) + 1

    return counts


def compare_reading_goals(counts, goals):
    """Compare the user's completed books against category goals."""
    completed_counts = {}

    for book in books_for_completed_counts:
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


def compare_goals(books, goals):
    """Compare completed books against reading goals."""
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
