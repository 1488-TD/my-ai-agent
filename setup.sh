#!/data/data/com.termux/files/usr/bin/bash
# One-shot setup for Android/Termux.
# Prompts for your free OpenRouter API key, writes .env,
# installs dependencies, and runs a quick test.

set -e
cd "$(dirname "$0")"

echo "=== AI Agent setup (Termux) ==="

# 1. .env file
if [ -f .env ]; then
  echo ".env already exists, keeping it."
else
  echo "Get a FREE key at https://openrouter.ai/keys"
  read -p "Paste your OpenRouter API key: " KEY
  if [ -z "$KEY" ]; then
    echo "No key entered. Create .env manually later. Skipping."
  else
    cat > .env << EOF
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_API_KEY=$KEY
LLM_MODEL=meta-llama/llama-3.2-3b-instruct:free
EOF
    echo ".env created."
  fi
fi

# 2. Dependencies
echo "Installing Python dependencies..."
pip install -q -r requirements.txt

# 3. Test
if [ -f .env ]; then
  echo ""
  echo "=== Testing the LLM connection ==="
  python stage2_llm.py
  echo ""
  echo "Setup done! Run the study assistant with:"
  echo "  python stage6_assistant.py"
else
  echo "Setup done, but add your .env before running (see README)."
fi
