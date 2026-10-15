"""Stage 3 — Build one tool.
Run: python stage3_tool.py
Learn: define get_time() and let the model request it via tool calling.
"""

from datetime import datetime

from llm import chat

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
    {"role": "system", "content": "You are a helpful assistant. Use tools for facts you don't know."},
    {"role": "user", "content": "What time is it right now?"},
]

message = chat(messages, tools=TOOLS)

# --- See if the model wanted to call our tool ---
if message.get("tool_calls"):
    call = message["tool_calls"][0]
    print("model asked for:", call["function"]["name"])
    if call["function"]["name"] == "get_time":
        result = get_time()
        print("tool result:", result)
else:
    print("model answered directly:", message["content"])
