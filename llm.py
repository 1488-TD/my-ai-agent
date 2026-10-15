"""Tiny LLM helper — zero dependencies (pure Python standard library).

Works with any OpenAI-compatible chat API, including OpenRouter.
Used by stages 2-6. Retries automatically on rate limits (429).
"""

import json
import os
import time
import urllib.error
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


def _request(base_url: str, payload: dict) -> dict:
    request = urllib.request.Request(
        base_url + "/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + os.environ.get("LLM_API_KEY", ""),
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=180) as response:
        return json.loads(response.read().decode("utf-8"))


def chat(messages: list, tools: list | None = None) -> dict:
    """Send messages to the LLM, return the assistant message as a dict.

    Retries up to 4 times on rate limits (429) or server errors (5xx),
    waiting between attempts. Shows the API's own error message otherwise.
    """
    load_env()
    base_url = os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1").rstrip("/")
    model = os.getenv("LLM_MODEL", "openrouter/free")

    payload = {"model": model, "messages": messages}
    if tools:
        payload["tools"] = tools

    last_error = None
    for attempt in range(4):
        try:
            data = _request(base_url, payload)
            return data["choices"][0]["message"]
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")
            try:
                body = json.loads(body).get("error", {}).get("message", body)
            except (ValueError, AttributeError):
                pass
            if e.code == 429 or e.code >= 500:
                wait = 15 * (attempt + 1)
                print(f"[rate-limited, waiting {wait}s... {body[:100]}]")
                time.sleep(wait)
                last_error = body
                continue
            raise SystemExit(f"API error {e.code}: {body}")
        except urllib.error.URLError as e:
            raise SystemExit(f"Connection error: {e.reason}")
    raise SystemExit(f"Still rate-limited after retries: {last_error}. Wait a minute and try again.")
