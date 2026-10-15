"""Stage 1 — Python basics.
Run: python stage1_basics.py
Learn: variables, functions, lists, dictionaries, loops, if statements.
"""

# --- Variables ---
name = "you"
goal = "building an AI agent from zero"
print(f"Hello {name}, today we are {goal}.")


# --- Functions ---
def greet(who: str) -> str:
    """A tiny function: takes input, returns output."""
    return f"Hi {who}!"


print(greet("agent builder"))


# --- Lists ---
skills = ["python", "prompts", "tools", "memory"]
for skill in skills:
    print(f"learning: {skill}")


# --- Dictionaries ---
agent_card = {
    "name": "MyAgent",
    "brain": "llama3.2",
    "tools": ["get_time", "add_note"],
}
print(agent_card["name"], "has", len(agent_card["tools"]), "tools")


# --- If statements ---
level = 1
if level == 0:
    print("zero")
elif level < 3:
    print("still early")
else:
    print("getting good")


# --- Putting it together: a mini "tool" ---
def word_count(text: str) -> int:
    return len(text.split())


print("word count:", word_count("the agent runs tools and loops"))
