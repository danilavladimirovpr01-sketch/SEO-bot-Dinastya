import os
from dotenv import load_dotenv

load_dotenv()

# Provider: "gemini" or "anthropic"
PROVIDER = os.getenv("PROVIDER", "gemini")

# Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.0-flash"

# Anthropic (for production)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL = "claude-sonnet-4-20250514"

MAX_TOKENS = 8192
