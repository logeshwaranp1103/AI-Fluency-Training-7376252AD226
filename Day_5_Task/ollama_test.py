import requests
import time

OLLAMA_URL = "http://localhost:11434"
MODEL = "student-expense"

def non_streaming(prompt):
    start = time.perf_counter()

    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        }
    )

    end = time.perf_counter()

    print("\n--- Non-Streaming ---")
    print("HTTP Status:", response.status_code)

    data = response.json()

    if "error" in data:
        print("Ollama Error:", data["error"])
        return

    print("Response:", data.get("response", "No response returned"))
    print(f"Total time: {end - start:.2f} seconds")

def streaming(prompt):
    start = time.perf_counter()
    first_token_time = None
    token_count = 0
    response_text = ""

    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": True
        },
        stream=True
    )

    for line in response.iter_lines():
        if line:
            import json

            data = json.loads(line)
            token = data.get("response", "")

            if token:
                if first_token_time is None:
                    first_token_time = time.perf_counter()

                print(token, end="", flush=True)
                response_text += token
                token_count += 1

            if data.get("done"):
                break

    end = time.perf_counter()

    ttft = first_token_time - start
    total_time = end - start
    tokens_per_second = token_count / (end - first_token_time)

    print("\n\n--- Streaming Metrics ---")
    print(f"Tokens: {token_count}")
    print(f"TTFT: {ttft:.2f} seconds")
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Tokens/second: {tokens_per_second:.2f}")


# Test prompts
prompts = [
    "How much did I spend on food?",
    "Give me a simple budget tip for a student.",
    "Should I reduce my entertainment spending?"
]

for prompt in prompts:
    print("\n================================")
    print("PROMPT:", prompt)
    print("================================")

    non_streaming(prompt)
    streaming(prompt)