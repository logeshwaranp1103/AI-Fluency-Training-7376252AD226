"""The single external tool used in the Day 3 task."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
EVENT_FILE = BASE_DIR / "event_info.txt"


def read_event_info() -> str:
    """Read the local college-event information and return it as plain text."""
    try:
        return EVENT_FILE.read_text(encoding="utf-8")
    except Exception as error:
        # Tool failures are returned as text so the agent can receive the observation
        # and decide how to respond instead of the whole program crashing.
        return f"Tool error: could not read event information: {type(error).__name__}: {error}"


TOOL_FUNCTIONS = {
    "read_event_info": read_event_info,
}

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_event_info",
            "description": (
                "Read the private local college event information. "
                "Use this tool when the user asks for factual details about the AI Workshop, "
                "such as its date, time, venue, fee, participant limit, deadline, or organizer."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    }
]


if __name__ == "__main__":
    print("=== Testing the one external tool ===")
    print(read_event_info())
