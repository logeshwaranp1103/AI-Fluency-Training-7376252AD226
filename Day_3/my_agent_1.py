"""Day 3: a ReAct agent written from scratch. Fixed for smaller models to read local files cleanly."""
import json
import sys
import os
import re
from html.parser import HTMLParser

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Day_1')))
from config import client, MODEL, banner
from my_tools import TOOLS, TOOL_FUNCTIONS

# FIXED: Custom HTML Parser that ignores internal CSS <style> data blocks completely
class HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.fed = []
        self.in_style = False

    def handle_starttag(self, tag, attrs):
        if tag == 'style':
            self.in_style = True

    def handle_endtag(self, tag):
        if tag == 'style':
            self.in_style = False

    def handle_data(self, d):
        if not self.in_style:
            self.fed.append(d)

    def get_data(self):
        # Cleans out extra newlines, duplicate spaces, and page headers
        text = " ".join("".join(self.fed).split())
        text = re.sub(r'Fee Notice\s*', '', text, flags=re.IGNORECASE)
        return text.strip()

# Instruct the model explicitly on how to pass local paths to read_webpage
SYSTEM_PROMPT = (
    "You are a college assistant. Use read_webpage to read any page or file the user "
    "mentions. If the file is local (like 'Day_3/notice.html'), pass that exact path "
    "as the url argument. Use calculator for every arithmetic step. "
    "Never guess a number that should come from a page. If no tool is needed, answer directly."
)

def agent(question, max_steps=6, verbose=True):
    messages = [{"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question}]

    for step in range(1, max_steps + 1):
        # 1. REASON
        response = client.chat.completions.create(
            model=MODEL, messages=messages, tools=TOOLS, temperature=0)
        message = response.choices[0].message

        # 2. STOP: no tool requested means the model has finished
        if not message.tool_calls:
            return message.content.strip()

        # 3. RECORD the model's request
        messages.append({
            "role": "assistant", "content": message.content or "",
            "tool_calls": [{"id": call.id, "type": "function",
                            "function": {"name": call.function.name,
                                         "arguments": call.function.arguments}}
                           for call in message.tool_calls]})

        # 4. ACT and 5. OBSERVE
        for call in message.tool_calls:
            name = call.function.name
            arguments = {}
            try:
                arguments = json.loads(call.function.arguments or "{}")
                
                # Intercept local file paths if the small 1.5B model tries to load them via read_webpage
                if name == "read_webpage":
                    url_val = arguments.get("url", "")
                    clean_path = url_val.replace("https://", "").replace("http://", "").replace("://example.com", "").replace("day3/", "")
                    
                    if "Day_3" in clean_path or "notice.html" in clean_path:
                        target_file = "Day_3/notice.html" if "notice.html" in clean_path else clean_path
                        if os.path.exists(target_file):
                            with open(target_file, "r", encoding="utf-8") as f:
                                raw_html = f.read()
                            
                            stripper = HTMLStripper()
                            stripper.feed(raw_html)
                            result = stripper.get_data()
                        else:
                            result = f"Error: Local file {target_file} not found."
                    else:
                        function = TOOL_FUNCTIONS.get(name)
                        result = function(**arguments) if function else f"Unknown tool: {name}"
                else:
                    function = TOOL_FUNCTIONS.get(name)
                    if function is None:
                        result = f"Unknown tool: {name}. Available: {list(TOOL_FUNCTIONS)}"
                    else:
                        result = function(**arguments)
            except json.JSONDecodeError as error:
                result = f"Argument error: {error}. Send valid JSON."
            except TypeError as error:
                result = f"Argument error: {error}"
            
            # FIXED: Conditionally hide the read_webpage output trace from showing up on the console
            if verbose:
                if name == "read_webpage":
                    print(f"   step {step}: [Reading local file content...]")
                else:
                    print(f"   step {step}: {name}({arguments}) -> {str(result)[:120]}")
            
            messages.append({"role": "tool", "tool_call_id": call.id, "content": str(result)})

    return "Stopped: maximum steps reached without a final answer."

if __name__ == "__main__":
    banner("MY AGENT (no guards)")

    # Question 1
    question = ("Read Day_3/notice.html and tell me the total fee for CS101 and AI202 "
                "after the merit scholarship.")
    print("Q:", question)
    print("A:", agent(question))

    # Question 2
    question = ("Read Day_3/notice.html and tell me the total fee for Hostel student, all three courses, including laboratory charges")
    print("Q:", question)
    print("A:", agent(question))

    # Question 3
    question = ("Read Day_3/notice.html and tell me What is 15% of the AI202 fee?")
    print("Q:", question)
    print("A:", agent(question))

    # Question 4
    question = ("Write a one-line welcome message for new students")
    print("Q:", question)
    print("A:", agent(question))
