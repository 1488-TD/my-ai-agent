"""Stage 2 — Connect to an LLM (zero dependencies).
Run: python stage2_llm.py
Learn: send a prompt to the model API and print the response.
"""

from llm import chat

messages = [
    {"role": "system", "content": "You are a helpful assistant. Be brief."},
    {"role": "user", "content": "Explain what an AI agent is in one sentence."},
]

message = chat(messages)
print(message["content"])
