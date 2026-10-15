# My First AI Agent

A simple AI agent built from zero, in 6 stages. No paid services required —
it works with a local Ollama model (free) or any OpenAI-compatible API.

## Stages

| Stage | File | What you learn |
|-------|------|----------------|
| 1 | `stage1_basics.py` | Python basics: variables, functions, lists, dicts, loops, if |
| 2 | `stage2_llm.py` | Send a prompt to an LLM and print the response |
| 3 | `stage3_tool.py` | Build one tool (`get_time`) the model can call |
| 4 | `stage4_loop.py` | The agent loop: handle tool calls until a final answer |
| 5 | `stage5_memory.py` | Conversation history + SQLite long-term memory |
| 6 | `stage6_assistant.py` | Real project: study assistant with several tools |

## Setup (100% free route)

1. Install Python 3.10+
2. Install Ollama: https://ollama.com/download
3. Pull a free model:
   ```
   ollama pull llama3.2
   ```
4. Install requirements:
   ```
   pip install -r requirements.txt
   ```
5. Copy `.env.example` to `.env` (Ollama route needs no API key)

## Run

```
python stage1_basics.py
python stage2_llm.py
python stage6_assistant.py
```

## Using OpenAI or OpenRouter instead

Set in `.env`:
```
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=sk-...
LLM_MODEL=gpt-4o-mini
```
(Ollama defaults are used if these are missing.)

## Push to GitHub

```
git init
git add .
git commit -m "My AI agent, built from zero"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```
