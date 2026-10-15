"""Tiny LLM helper — zero dependencies (pure Python standard library).

Works with any OpenAI-compatible chat API, including OpenRouter.
Used by stages 2-6.
"""

import json
import os
import urllib.request

ENV_LOADED = False


def load_env(path: str = ".env") -> None:
    """Load a .env file (KEY=VALUE lines) into environment variables."""
    global ENV_LOADED
    if ENV_LOADED or not os.path.exists(path):
        ENV_LOADED = True
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())
    ENV_LOADED = True


def chat(messages: list, tools: list | None = None) -> dict:
    """Send messages to the LLM, return the assistant message as a dict.

    The dict has 'content' (str or None) and possibly 'tool_calls'
    (list of {'id':..., 'function': {'name':..., 'arguments': '<json str>'}}).
    """
    load_env()
    base_url = os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1").rstrip("/")
    api_key = os.getenv("LLM_API_KEY", "")
    model = os.getenv("LLM_MODEL", "google/gemma-4-31b-it:free")

    payload = {"model": model, "messages": messages}
    if tools:
        payload["tools"] = tools

    request = urllib.request.Request(
        base_url + "/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + api_key,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=180) as response:
        data = json.loads(response.read().decode("utf-8"))
    return data["choices"][0]["message"]
