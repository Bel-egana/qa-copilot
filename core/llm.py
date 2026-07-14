"""Thin wrapper around the Anthropic Messages API."""

import os

import anthropic
from dotenv import load_dotenv

load_dotenv()

# Display name -> model ID. Haiku is the default: ~1-2 cents per full analysis.
MODELS = {
    "Claude Haiku 4.5 — fast & cheap": "claude-haiku-4-5",
    "Claude Sonnet 5 — higher quality": "claude-sonnet-5",
}
DEFAULT_MODEL = "claude-haiku-4-5"

_PLACEHOLDER = "your-api-key-here"


class LLMError(Exception):
    """Human-readable error to show in the UI (never a stack trace)."""


def get_api_key() -> str | None:
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not key or key == _PLACEHOLDER:
        return None
    return key


def generate(prompt: str, model: str = DEFAULT_MODEL, max_tokens: int = 8000) -> str:
    api_key = get_api_key()
    if api_key is None:
        raise LLMError(
            "No API key found. Copy `.env.example` to `.env` and paste your key "
            "from https://console.anthropic.com"
        )

    client = anthropic.Anthropic(api_key=api_key)
    try:
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
    except anthropic.AuthenticationError:
        raise LLMError("The API key was rejected. Check the key in your `.env` file.")
    except anthropic.RateLimitError:
        raise LLMError("Rate limit reached. Wait a minute and try again.")
    except anthropic.APIConnectionError:
        raise LLMError("Could not reach the Anthropic API. Check your internet connection.")
    except anthropic.APIStatusError as exc:
        raise LLMError(f"The API returned an error (HTTP {exc.status_code}). Try again later.")

    # Sonnet 5 may prepend thinking blocks; keep only text blocks.
    return "".join(block.text for block in response.content if block.type == "text")
