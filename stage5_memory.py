"""Stage 5 — Add memory.
Run: python stage5_memory.py
Learn: short-term memory (full chat history) + long-term memory (SQLite).
"""

import json
import os
import sqlite3
from datetime import datetime

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url=os.getenv("LLM_BASE_URL", "http://localhost:11434/v1"),
    api_key=os.getenv("LLM_API_KEY", "ollama"),
)
MODEL = os.getenv("LLM_MODEL", "llama3.2")

# --- Long-term memory: SQLite ---
DB_PATH = os.path.join(os.path.dirname(__file__), "memory.db")


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


def list_memory_keys(conn: sqlite3.Connection) -> str:
    rows = conn.execute("SELECT key FROM memories ORDER BY key").fetchall()
    return ", ".join(r[0] for r in rows) if rows else "no memories yet"


# --- Tools exposed to the model ---
def get_time() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


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
    if name == "get_time":
        return get_time()
    return "error: unknown tool"


def agent_loop(conn: sqlite3.Connection, messages: list) -> str:
    """messages persists between calls = short-term memory."""
    while True:
        response = client.chat.completions.create(
            model=MODEL, messages=messages, tools=TOOL_SCHEMAS
        )
        msg = response.choices[0].message
        if not msg.tool_calls:
            messages.append({"role": "assistant", "content": msg.content})
            return msg.content
        for call in msg.tool_calls:
            args = json.loads(call.function.arguments or "{}")
            result = run_tool(conn, call.function.name, args)
            print(f"[tool] {call.function.name}({args}) -> {result}")
            messages.append(msg)
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})


if __name__ == "__main__":
    conn = init_db()
    history = [
        {"role": "system", "content": "You are a personal assistant with memory tools."}
    ]

    # First conversation: the agent stores a fact
    print("you: My favorite language is Python")
    history.append({"role": "user", "content": "My favorite language is Python, remember that."})
    print("agent:", agent_loop(conn, history))

    # Second conversation: same history, so it remembers the context;
    # and it can use recall() for facts stored in SQLite
    print("\nyou: What is my favorite language?")
    history.append({"role": "user", "content": "What is my favorite language? Check your memory."})
    print("agent:", agent_loop(conn, history))

    conn.close()
    print("\nSQLite memories:", list_memory_keys(init_db()))
