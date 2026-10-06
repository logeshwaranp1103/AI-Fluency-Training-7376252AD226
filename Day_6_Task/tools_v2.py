"""Day 6: student expense and budget tools with strict JSON schemas."""

import ast
import operator

EXPENSES = [
    {"date": "2026-09-02", "category": "Food", "description": "College canteen", "amount": 120},
    {"date": "2026-09-04", "category": "Transport", "description": "Bus", "amount": 80},
    {"date": "2026-09-05", "category": "Food", "description": "Lunch", "amount": 180},
    {"date": "2026-09-07", "category": "Entertainment", "description": "Movie", "amount": 350},
    {"date": "2026-09-09", "category": "Education", "description": "Books", "amount": 600},
    {"date": "2026-09-11", "category": "Transport", "description": "Bus", "amount": 70},
    {"date": "2026-09-13", "category": "Food", "description": "Snacks", "amount": 100},
]

BUDGETS = {
    "Food": 400,
    "Transport": 200,
    "Entertainment": 300,
    "Education": 700,
}

CATEGORIES = list(BUDGETS)

def get_spending(category: str) -> str:
    """Return total spending for one category."""
    normalized = category.strip().title()
    if normalized not in BUDGETS:
        return f"Unknown category: {category}. Valid categories: {', '.join(CATEGORIES)}"
    total = sum(item["amount"] for item in EXPENSES if item["category"] == normalized)
    return str(total)

def get_budget(category: str) -> str:
    """Return the monthly budget for one category."""
    normalized = category.strip().title()
    if normalized not in BUDGETS:
        return f"Unknown category: {category}. Valid categories: {', '.join(CATEGORIES)}"
    return str(BUDGETS[normalized])

_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
}

def _evaluate(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_evaluate(node.left), _evaluate(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_evaluate(node.operand))
    raise ValueError("Unsupported expression")

def calculator(expression: str) -> str:
    """Evaluate a basic arithmetic expression safely."""
    try:
        return str(_evaluate(ast.parse(expression, mode="eval").body))
    except Exception as error:
        return f"Calculator error: {error}. Use only numbers and + - * / ( )."

TOOL_FUNCTIONS = {
    "get_spending": get_spending,
    "get_budget": get_budget,
    "calculator": calculator,
}

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_spending",
            "description": (
                "Get total student spending for ONE category. "
                "Valid categories: Food, Transport, Entertainment, Education."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": CATEGORIES,
                        "description": "One spending category."
                    }
                },
                "required": ["category"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_budget",
            "description": (
                "Get the monthly student budget for ONE category. "
                "Valid categories: Food, Transport, Entertainment, Education."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": CATEGORIES,
                        "description": "One budget category."
                    }
                },
                "required": ["category"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": (
                "Calculate one arithmetic expression using numbers and + - * / "
                "and brackets. Example: 400 - 500."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Arithmetic expression using numbers and operators only."
                    }
                },
                "required": ["expression"],
                "additionalProperties": False,
            },
        },
    },
]

# One source of truth used both for the API request and local validation.
SCHEMAS = {tool["function"]["name"]: tool["function"]["parameters"] for tool in TOOLS}

if __name__ == "__main__":
    print("Tools:", ", ".join(TOOL_FUNCTIONS))
    print("Schemas:", list(SCHEMAS))
    print("Food spending:", get_spending("Food"))
    print("Food budget:", get_budget("Food"))
