from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

response = client.chat.completions.create(
    model="student-expense",
    messages=[
        {
            "role": "system",
            "content": "You are a friendly teacher. Explain everything in very simple English."
        },
        {
            "role": "user",
            "content": "What is a budget?"
        }
    ]
)

print(response.choices[0].message.content)