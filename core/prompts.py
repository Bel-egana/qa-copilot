"""Load prompt templates from the prompts/ folder and fill placeholders."""

from pathlib import Path

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


def load_prompt(name: str) -> str:
    path = PROMPTS_DIR / f"{name}.md"
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    return path.read_text(encoding="utf-8")


def render_prompt(name: str, **values: str) -> str:
    # Plain string replace (not str.format) so literal {braces} in
    # prompt bodies — JSON examples, Gherkin — never break rendering.
    text = load_prompt(name)
    for key, value in values.items():
        text = text.replace("{" + key + "}", value)
    return text
