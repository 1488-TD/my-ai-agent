"""Stage 4 — Build the agent loop.
Run: python stage4_loop.py
Learn: the heart of every agent. Send prompt -> model picks tools ->
run tools -> feed results back -> repeat until a final answer.
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


# --- Tools: the functions the agent is allowed to call ---
def get_time() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def calculator(expression: str) -> str:
    """Safe-ish eval: digits and math operators only."""
    allowed = set("0123456789+-*/(). ")
    if not set(expression) <= allowed:
        return "error: invalid characters"
    return str(eval(expression))


TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "Returns the current local date and time.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Evaluates a basic math expression, e.g. '23*7+5'.",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string"}},
                "required": ["expression"],
            },
        },
    },
]

# Registry: name -> actual python function
TOOL_REGISTRY = {"get_time": get_time, "calculator": calculator}


def run_tool(name: str, arguments_json: str) -> str:
    """Execute a tool by name and return its result as a string."""
    func = TOOL_REGISTRY.get(name)
    if func is None:
        return f"error: unknown tool {name}"
    args = json.loads(arguments_json) if arguments_json else {}
    return str(func(**args))


def agent_loop(user_message: str) -> str:
    """The agent loop: keep going until the model produces a final answer."""
    messages = [
        {"role": "system", "content": "You are a helpful assistant. Use your tools when they help."},
        {"role": "user", "content": user_message},
    ]

    while True:
        response = client.chat.completions.create(
            model=MODEL, messages=messages, tools=TOOL_SCHEMAS
        )
        msg = response.choices[0].message

        # No tool calls = final answer, we are done
        if not msg.tool_calls:
            return msg.content

        # The model wants tools: run each one, append the results
        for call in msg.tool_calls:
            result = run_tool(call.function.name, call.function.arguments)
            print(f"[tool] {call.function.name}({call.function.arguments}) -> {result}")
            messages.append(msg)  # the model's tool request
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})


if __name__ == "__main__":
    question = "What time is it, and what is 23*7+5?"
    print("user:", question)
    print("agent:", agent_loop(question))
