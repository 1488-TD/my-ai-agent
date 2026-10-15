"""Stage 3 — Build one tool.
Run: python stage3_tool.py
Learn: define get_time() and let the model request it via function calling.
"""

import json
import os
from datetime import datetime

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url=os.getenv("LLM_BASE_URL", "http://localhost:11434/v1"),
    api_key=os.getenv("LLM_API_KEY", "ollama"),
)
MODEL = os.getenv("LLM_MODEL", "llama3.2")

# --- The tool: a plain Python function ---
def get_time() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# --- The tool's schema: tells the model what exists and how to call it ---
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "Returns the current local date and time.",
            "parameters": {"type": "object", "properties": {}},
        },
    }
]

messages = [
    {"role": "system", "content": "You are a helpful assistant. Use tools when asked about facts you don't know."},
    {"role": "user", "content": "What time is it right now?"},
]

response = client.chat.completions.create(model=MODEL, messages=messages, tools=TOOLS)
msg = response.choices[0].message

# --- See if the model wanted to call our tool ---
if msg.tool_calls:
    call = msg.tool_calls[0]
    print("model asked for:", call.function.name)
    if call.function.name == "get_time":
        result = get_time()
        print("tool result:", result)
else:
    print("model answered directly:", msg.content)
