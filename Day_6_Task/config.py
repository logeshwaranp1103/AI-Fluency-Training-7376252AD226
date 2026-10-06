"""Configuration for Day 6 Reliable Tool Calling lab."""
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

PROVIDER = os.getenv("PROVIDER", "ollama").lower()
MODEL = os.getenv("MODEL", "qwen3:8b")

BASE_URLS = {
    "ollama": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
    "groq": "https://api.groq.com/openai/v1",
    "huggingface": "https://router.huggingface.co/v1",
}

base_url = os.getenv("OPENAI_BASE_URL", BASE_URLS.get(PROVIDER, BASE_URLS["ollama"]))
api_key = os.getenv("OPENAI_API_KEY", "ollama")

client = OpenAI(base_url=base_url, api_key=api_key)

def banner(title: str) -> None:
    print("=" * 78)
    print(f"{title} | provider: {PROVIDER} | model: {MODEL}")
    print("=" * 78)
