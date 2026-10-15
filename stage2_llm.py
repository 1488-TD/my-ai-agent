"""Stage 2 — Connect to an LLM.
Run: python stage2_llm.py
Learn: send a prompt, print the response. Works with Ollama (free) or any
OpenAI-compatible API (OpenAI, OpenRouter, etc.).
"""

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url=os.getenv("LLM_BASE_URL", "http://localhost:11434/v1"),
    api_key=os.getenv("LLM_API_KEY", "ollama"),  # Ollama ignores the key
)

MODEL = os.getenv("LLM_MODEL", "llama3.2")

messages = [
    {"role": "system", "content": "You are a helpful assistant. Be brief."},
    {"role": "user", "content": "Explain what an AI agent is in one sentence."},
]

response = client.chat.completions.create(model=MODEL, messages=messages)
print(response.choices[0].message.content)
