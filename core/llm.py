"""Thin wrapper around the Google Gemini API (free tier)."""

import os

from dotenv import load_dotenv
from google import genai
from google.genai import errors as genai_errors

load_dotenv()

# Display name -> model ID. Both are available on the free tier;
# Flash has the most generous free limits.
MODELS = {
    "Gemini 3.5 Flash — best quality on the free tier": "gemini-3.5-flash",
    "Gemini 3.1 Flash Lite — fastest": "gemini-3.1-flash-lite",
}
DEFAULT_MODEL = "gemini-3.5-flash"

_PLACEHOLDER = "your-api-key-here"


class LLMError(Exception):
    """Human-readable error to show in the UI (never a stack trace)."""


def get_api_key() -> str | None:
    key = os.environ.get("GOOGLE_API_KEY", "").strip()
    if not key or key == _PLACEHOLDER:
        return None
    return key


def generate(prompt: str, model: str = DEFAULT_MODEL) -> str:
    api_key = get_api_key()
    if api_key is None:
        raise LLMError(
            "No API key found. Create a free key at https://aistudio.google.com, "
            "then copy `.env.example` to `.env` and paste it there."
        )

    client = genai.Client(api_key=api_key)
    try:
        response = client.models.generate_content(model=model, contents=prompt)
    except genai_errors.APIError as exc:
        if exc.code == 429:
            raise LLMError(
                "Free tier limit reached. Wait a minute and try again "
                "(or switch to Gemini 2.5 Flash, which has higher free limits)."
            )
        if exc.code in (401, 403):
            raise LLMError("The API key was rejected. Check the key in your `.env` file.")
        raise LLMError(f"The API returned an error (HTTP {exc.code}). Try again later.")
    except Exception:
        raise LLMError("Could not reach the Gemini API. Check your internet connection.")

    if not response.text:
        raise LLMError("The model returned an empty response. Try again.")
    return response.text
