"""Stage 6 — Real project: Study Assistant.
Run: python stage6_assistant.py
An interactive study assistant with several tools:
  calculator, add_note, list_notes, save_quiz, quiz_me
Short-term memory: the chat loop below.
Long-term memory: notes + quiz terms stored in SQLite.
Type 'quit' to exit.
"""

import json
import sqlite3
from datetime import datetime

from llm import chat

DB_PATH = "study.db"


def init_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS notes ("
        " id INTEGER PRIMARY KEY AUTOINCREMENT,"
        " topic TEXT NOT NULL,"
        " content TEXT NOT NULL,"
        " created_at TEXT NOT NULL)"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS quiz ("
        " id INTEGER PRIMARY KEY AUTOINCREMENT,"
        " question TEXT NOT NULL,"
        " answer TEXT NOT NULL)"
    )
    conn.commit()
    return conn


# --- Tools ---
def calculator(expression: str) -> str:
    allowed = set("0123456789+-*/(). ")
    if not set(expression) <= allowed:
        return "error: invalid characters"
    return str(eval(expression))


def add_note(conn, topic: str, content: str) -> str:
    conn.execute(
        "INSERT INTO notes (topic, content, created_at) VALUES (?, ?, ?)",
        (topic, content, datetime.now().isoformat()),
    )
    conn.commit()
    return f"note saved under '{topic}'"


def list_notes(conn) -> str:
    rows = conn.execute("SELECT topic, content FROM notes").fetchall()
    return "\n".join(f"- {t}: {c}" for t, c in rows) or "no notes yet"


def save_quiz(conn, question: str, answer: str) -> str:
    conn.execute("INSERT INTO quiz (question, answer) VALUES (?, ?)", (question, answer))
    conn.commit()
    return "quiz item saved"


def quiz_me(conn) -> str:
    row = conn.execute("SELECT question, answer FROM quiz ORDER BY RANDOM() LIMIT 1").fetchone()
    if row is None:
        return "no quiz items saved yet"
    return f"Q: {row[0]}\n(answer: {row[1]})"


TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Evaluates a basic math expression.",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string"}},
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_note",
            "description": "Save a study note under a topic.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["topic", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_notes",
            "description": "List all saved study notes.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "save_quiz",
            "description": "Save a flashcard question + answer for later self-testing.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {"type": "string"},
                    "answer": {"type": "string"},
                },
                "required": ["question", "answer"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "quiz_me",
            "description": "Return a random saved flashcard question to test the user.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]


def make_runner(conn):
    def run_tool(name: str, args: dict) -> str:
        handlers = {
            "calculator": lambda: calculator(args["expression"]),
            "add_note": lambda: add_note(conn, args["topic"], args["content"]),
            "list_notes": lambda: list_notes(conn),
            "save_quiz": lambda: save_quiz(conn, args["question"], args["answer"]),
            "quiz_me": lambda: quiz_me(conn),
        }
        handler = handlers.get(name)
        return handler() if handler else "error: unknown tool"

    return run_tool


def agent_loop(conn, run_tool, messages) -> str:
    while True:
        message = chat(messages, tools=TOOL_SCHEMAS)
        if not message.get("tool_calls"):
            messages.append({"role": "assistant", "content": message["content"]})
            return message["content"]
        for call in message["tool_calls"]:
            args = json.loads(call["function"]["arguments"] or "{}")
            result = run_tool(call["function"]["name"], args)
            print(f"  [tool] {call['function']['name']} -> {result[:80]}")
            messages.append(message)
            messages.append({"role": "tool", "tool_call_id": call["id"], "content": result})


SYSTEM_PROMPT = (
    "You are a study assistant. Help the user learn any topic: explain clearly, "
    "save important points as notes with add_note, create flashcards with save_quiz, "
    "test the user with quiz_me, and use the calculator for math. Be encouraging."
)


def main() -> None:
    conn = init_db()
    run_tool = make_runner(conn)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    print("Study Assistant ready. Type 'quit' to exit.\n")

    while True:
        try:
            user_input = input("you: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not user_input or user_input.lower() in {"quit", "exit"}:
            print("bye! your notes are saved in study.db")
            break
        messages.append({"role": "user", "content": user_input})
        print("assistant:", agent_loop(conn, run_tool, messages))

    conn.close()


if __name__ == "__main__":
    main()
