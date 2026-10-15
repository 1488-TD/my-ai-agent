"""Stage 5 — Add memory.
Run: python stage5_memory.py
Learn: short-term memory (full chat history) + long-term memory (SQLite).
"""

import json
import sqlite3
from datetime import datetime

from llm import chat

# --- Long-term memory: SQLite ---
DB_PATH = "memory.db"


def init_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS memories ("
        " id INTEGER PRIMARY KEY AUTOINCREMENT,"
        " key TEXT UNIQUE NOT NULL,"
        " value TEXT NOT NULL,"
        " created_at TEXT NOT NULL)"
    )
    conn.commit()
    return conn


def save_memory(conn: sqlite3.Connection, key: str, value: str) -> str:
    conn.execute(
        "INSERT INTO memories (key, value, created_at) VALUES (?, ?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, value, datetime.now().isoformat()),
    )
    conn.commit()
    return f"saved {key}"


def recall(conn: sqlite3.Connection, key: str) -> str:
    row = conn.execute("SELECT value FROM memories WHERE key=?", (key,)).fetchone()
    return row[0] if row else "not found"


TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "save_memory",
            "description": "Store a fact for later (long-term memory).",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "short label, e.g. 'favorite_language'"},
                    "value": {"type": "string"},
                },
                "required": ["key", "value"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "recall",
            "description": "Retrieve a stored fact by its key.",
            "parameters": {
                "type": "object",
                "properties": {"key": {"type": "string"}},
                "required": ["key"],
            },
        },
    },
]


def run_tool(conn: sqlite3.Connection, name: str, args: dict) -> str:
    if name == "save_memory":
        return save_memory(conn, args["key"], args["value"])
    if name == "recall":
        return recall(conn, args["key"])
    return "error: unknown tool"


def agent_loop(conn: sqlite3.Connection, messages: list) -> str:
    """messages persists between calls = short-term memory."""
    while True:
        message = chat(messages, tools=TOOL_SCHEMAS)
        if not message.get("tool_calls"):
            messages.append({"role": "assistant", "content": message["content"]})
            return message["content"]
        for call in message["tool_calls"]:
            args = json.loads(call["function"]["arguments"] or "{}")
            result = run_tool(conn, call["function"]["name"], args)
            print(f"[tool] {call['function']['name']}({args}) -> {result}")
            messages.append(message)
            messages.append({"role": "tool", "tool_call_id": call["id"], "content": result})


if __name__ == "__main__":
    conn = init_db()
    history = [
        {"role": "system", "content": "You are a personal assistant with memory tools."}
    ]

    # First: the agent stores a fact
    print("you: My favorite language is Python, remember that.")
    history.append({"role": "user", "content": "My favorite language is Python, remember that."})
    print("agent:", agent_loop(conn, history))

    # Second: it can use recall() for facts stored in SQLite
    print("\nyou: What is my favorite language?")
    history.append({"role": "user", "content": "What is my favorite language? Check your memory."})
    print("agent:", agent_loop(conn, history))

    conn.close()
