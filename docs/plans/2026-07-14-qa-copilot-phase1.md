# QA Copilot Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A local Streamlit app that analyzes user stories, finds gaps, generates test cases, and writes bug reports using the Anthropic API — a polished QA portfolio project.

**Architecture:** Thin Streamlit UI (`app.py`) over a small core: `core/prompts.py` loads Markdown prompt templates from `prompts/` and fills placeholders; `core/llm.py` wraps the Anthropic Messages API; `core/export.py` converts Markdown tables to CSV for download. Prompts live as visible `.md` files so the repo doubles as a prompt library.

**Tech Stack:** Python 3.11+, Streamlit, `anthropic` SDK, `python-dotenv`, pytest.

**Working directory:** `D:\qa-copilot` (all paths below are relative to it). Git identity is already configured locally. Spec: `docs/specs/2026-07-14-qa-copilot-phase1-design.md`.

---

### Task 1: Project scaffolding

**Files:**
- Create: `.gitignore`
- Create: `requirements.txt`
- Create: `.env.example`
- Create: `core/__init__.py` (empty)
- Create: `tests/__init__.py` (empty)

- [ ] **Step 1: Create `.gitignore`**

```gitignore
# Secrets — never commit the real API key
.env

# Python
__pycache__/
*.py[cod]
.pytest_cache/
venv/
.venv/

# Streamlit
.streamlit/secrets.toml

# OS
Thumbs.db
.DS_Store
```

- [ ] **Step 2: Create `requirements.txt`**

```
streamlit>=1.37
anthropic>=0.40
python-dotenv>=1.0
pytest>=8.0
```

- [ ] **Step 3: Create `.env.example`**

```
# Copy this file to .env and paste your real key from https://console.anthropic.com
ANTHROPIC_API_KEY=your-api-key-here
```

- [ ] **Step 4: Create empty package markers**

Create `core/__init__.py` and `tests/__init__.py`, both empty files.

- [ ] **Step 5: Install dependencies**

Run: `python -m pip install -r requirements.txt`
Expected: all packages install without errors (most may already be present).

- [ ] **Step 6: Commit**

```bash
git add .gitignore requirements.txt .env.example core/__init__.py tests/__init__.py
git commit -m "chore: project scaffolding (gitignore, deps, env template)"
```

---

### Task 2: Prompt loader (`core/prompts.py`) — TDD

**Files:**
- Create: `core/prompts.py`
- Test: `tests/test_prompts.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_prompts.py`:

```python
from pathlib import Path

import pytest

from core import prompts


def test_prompts_dir_points_to_repo_prompts_folder():
    assert prompts.PROMPTS_DIR.name == "prompts"
    assert prompts.PROMPTS_DIR.parent == Path(__file__).resolve().parent.parent


def test_render_prompt_fills_placeholders(tmp_path, monkeypatch):
    (tmp_path / "demo.md").write_text(
        "Analyze in {language} at {detail_level} level:\n\n{input}",
        encoding="utf-8",
    )
    monkeypatch.setattr(prompts, "PROMPTS_DIR", tmp_path)

    result = prompts.render_prompt(
        "demo", input="my story", language="Spanish", detail_level="junior"
    )

    assert result == "Analyze in Spanish at junior level:\n\nmy story"


def test_render_prompt_leaves_literal_braces_alone(tmp_path, monkeypatch):
    # Prompt files may contain JSON or Gherkin braces that are NOT placeholders
    (tmp_path / "demo.md").write_text('{"key": "value"} {input}', encoding="utf-8")
    monkeypatch.setattr(prompts, "PROMPTS_DIR", tmp_path)

    result = prompts.render_prompt("demo", input="X")

    assert result == '{"key": "value"} X'


def test_load_prompt_missing_file_raises(tmp_path, monkeypatch):
    monkeypatch.setattr(prompts, "PROMPTS_DIR", tmp_path)
    with pytest.raises(FileNotFoundError):
        prompts.load_prompt("does_not_exist")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_prompts.py -v`
Expected: FAIL with `ImportError` / `ModuleNotFoundError` (module `core.prompts` does not exist).

- [ ] **Step 3: Write the implementation**

Create `core/prompts.py`:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_prompts.py -v`
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add core/prompts.py tests/test_prompts.py
git commit -m "feat: prompt template loader with placeholder rendering"
```

---

### Task 3: The four prompt templates

**Files:**
- Create: `prompts/analyze_story.md`
- Create: `prompts/find_gaps.md`
- Create: `prompts/test_cases.md`
- Create: `prompts/bug_report.md`
- Test: `tests/test_prompt_files.py`

All four templates use exactly three placeholders: `{input}`, `{language}`, `{detail_level}`.

- [ ] **Step 1: Write the failing test**

Create `tests/test_prompt_files.py`:

```python
import pytest

from core import prompts

PROMPT_NAMES = ["analyze_story", "find_gaps", "test_cases", "bug_report"]


@pytest.mark.parametrize("name", PROMPT_NAMES)
def test_prompt_file_exists_and_has_placeholders(name):
    text = prompts.load_prompt(name)
    for placeholder in ("{input}", "{language}", "{detail_level}"):
        assert placeholder in text, f"{name}.md is missing {placeholder}"


@pytest.mark.parametrize("name", PROMPT_NAMES)
def test_prompt_renders_without_leftover_placeholders(name):
    rendered = prompts.render_prompt(
        name, input="sample", language="English", detail_level="junior"
    )
    for placeholder in ("{input}", "{language}", "{detail_level}"):
        assert placeholder not in rendered
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_prompt_files.py -v`
Expected: FAIL with `FileNotFoundError` for each prompt.

- [ ] **Step 3: Create `prompts/analyze_story.md`**

````markdown
# Role

You are a senior QA analyst reviewing a user story before the team commits to it.

# Instructions

- Write your entire response in **{language}**.
- Detail level: **{detail_level}**. If "junior", explain your reasoning in plain terms so someone new to QA learns from it. If "senior", be concise and skip explanations of basic concepts.
- Base everything strictly on the story text. Where the story is silent, say so — do not invent requirements.
- Respond in well-formatted Markdown using the structure below.

# Output structure

## Summary
2-3 sentences: what this story delivers and for whom.

## Acceptance criteria
List the acceptance criteria you can extract from the story (explicit or clearly implied). If none are stated, say so explicitly.

## INVEST assessment
A Markdown table with one row per INVEST criterion (Independent, Negotiable, Valuable, Estimable, Small, Testable). Columns: Criterion | Verdict (✅ / ⚠️ / ❌) | Justification.

## Testability verdict
One short paragraph: can QA start designing tests from this story as written? What is the single biggest blocker, if any?

# User story to analyze

{input}
````

- [ ] **Step 4: Create `prompts/find_gaps.md`**

````markdown
# Role

You are a senior QA analyst doing a gap analysis on a user story. Your job is to find what is missing, ambiguous, or risky BEFORE development starts.

# Instructions

- Write your entire response in **{language}**.
- Detail level: **{detail_level}**. If "junior", explain why each gap matters. If "senior", state gaps concisely.
- Only report real gaps grounded in the story text. Do not pad the list — if the story is unusually complete, say so.
- Respond in well-formatted Markdown using the structure below.

# Output structure

## Ambiguities
Statements in the story that can be interpreted in more than one way. Quote the ambiguous wording.

## Missing acceptance criteria
Behaviors the story implies but never specifies (validations, limits, permissions, error states).

## Edge cases not covered
Concrete edge cases a tester would probe: boundary values, empty/invalid input, concurrency, connectivity, roles, localization — whichever genuinely apply to THIS story.

## Questions for the Product Owner
A numbered list of the questions a QA should ask before testing, ordered by importance. Make each question specific and answerable.

# User story to analyze

{input}
````

- [ ] **Step 5: Create `prompts/test_cases.md`**

````markdown
# Role

You are a senior QA analyst designing test cases from a user story.

# Instructions

- Write your entire response in **{language}** (keep Gherkin keywords Given/When/Then in English, as is standard).
- Detail level: **{detail_level}**. If "junior", add a short note per section explaining the coverage strategy. If "senior", output the artifacts only.
- Cover: happy path, negative cases, and edge cases. Derive everything from the story; if the story lacks detail for a case, mark the assumption explicitly with "(assumption)".
- Respond in well-formatted Markdown using the structure below.

# Output structure

## Coverage overview
One short paragraph: what you covered and what you deliberately left out (e.g. non-functional testing).

## Gherkin scenarios
For each scenario use:

```gherkin
Scenario: <name>
  Given <precondition>
  When <action>
  Then <expected result>
```

## Test case table
A single Markdown table with EXACTLY these columns:

| ID | Title | Priority | Preconditions | Steps | Expected result |

Rules for the table:
- ID format: TC-001, TC-002, ...
- Priority: High / Medium / Low.
- Steps: numbered inside the cell, separated by `<br>`.
- Do not use the pipe character `|` inside any cell content.

# User story

{input}
````

- [ ] **Step 6: Create `prompts/bug_report.md`**

````markdown
# Role

You are a senior QA analyst turning an informal defect description into a professional bug report ready to be filed in an issue tracker.

# Instructions

- Write your entire response in **{language}**.
- Detail level: **{detail_level}**. If "junior", add a closing note explaining how you chose severity and priority. If "senior", output the report only.
- Use only the information provided. Where a required field is unknown (environment, version), write "To be completed" — never invent data.
- If the description is too vague to reproduce, still produce the report and list what is missing under "Additional notes".
- Respond in well-formatted Markdown using the structure below.

# Output structure

## <Bug title — concise, starts with the affected feature>

| Field | Value |
|---|---|
| Severity | Critical / Major / Minor / Trivial |
| Priority | High / Medium / Low |
| Environment | To be completed by the reporter if not stated |

### Steps to reproduce
Numbered steps, starting from a clean state.

### Actual result
What happens.

### Expected result
What should happen instead.

### Additional notes
Missing information, suspected cause, related areas worth regression-testing.

# Informal bug description

{input}
````

- [ ] **Step 7: Run tests to verify they pass**

Run: `python -m pytest tests/test_prompt_files.py -v`
Expected: 8 passed.

- [ ] **Step 8: Commit**

```bash
git add prompts/ tests/test_prompt_files.py
git commit -m "feat: QA prompt library (analysis, gaps, test cases, bug report)"
```

---

### Task 4: CSV export (`core/export.py`) — TDD

**Files:**
- Create: `core/export.py`
- Test: `tests/test_export.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_export.py`:

```python
from core.export import markdown_table_to_csv


def test_converts_simple_table():
    md = (
        "Some intro text\n"
        "\n"
        "| ID | Title |\n"
        "|---|---|\n"
        "| TC-001 | Login ok |\n"
        "| TC-002 | Login fails |\n"
        "\n"
        "Trailing text"
    )
    csv_text = markdown_table_to_csv(md)
    lines = csv_text.strip().splitlines()
    assert lines[0] == "ID,Title"
    assert lines[1] == "TC-001,Login ok"
    assert lines[2] == "TC-002,Login fails"


def test_quotes_cells_containing_commas():
    md = "| ID | Steps |\n|---|---|\n| TC-001 | Open, click, wait |\n"
    csv_text = markdown_table_to_csv(md)
    assert '"Open, click, wait"' in csv_text


def test_returns_empty_string_when_no_table():
    assert markdown_table_to_csv("Just prose, no table here.") == ""


def test_only_first_table_is_converted():
    md = (
        "| A |\n|---|\n| 1 |\n"
        "\n"
        "| B |\n|---|\n| 2 |\n"
    )
    csv_text = markdown_table_to_csv(md)
    assert "1" in csv_text
    assert "2" not in csv_text
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_export.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'core.export'`.

- [ ] **Step 3: Write the implementation**

Create `core/export.py`:

```python
"""Convert the first Markdown table in a text into CSV for download."""

import csv
import io


def _is_separator_row(cells: list[str]) -> bool:
    return all(cell and set(cell) <= set("-: ") for cell in cells)


def markdown_table_to_csv(markdown: str) -> str:
    rows: list[list[str]] = []
    in_table = False

    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if line.startswith("|") and line.endswith("|") and len(line) > 1:
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if _is_separator_row(cells):
                continue
            rows.append(cells)
            in_table = True
        elif in_table:
            break  # first table ended

    if not rows:
        return ""

    buffer = io.StringIO()
    csv.writer(buffer, lineterminator="\n").writerows(rows)
    return buffer.getvalue()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_export.py -v`
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add core/export.py tests/test_export.py
git commit -m "feat: markdown table to CSV export"
```

---

### Task 5: Anthropic API wrapper (`core/llm.py`) — TDD on the non-network parts

**Files:**
- Create: `core/llm.py`
- Test: `tests/test_llm.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_llm.py`:

```python
import pytest

from core import llm


def test_get_api_key_returns_none_when_missing(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert llm.get_api_key() is None


def test_get_api_key_returns_none_for_placeholder(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "your-api-key-here")
    assert llm.get_api_key() is None


def test_get_api_key_returns_trimmed_key(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "  sk-ant-test123  ")
    assert llm.get_api_key() == "sk-ant-test123"


def test_generate_raises_llm_error_without_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(llm.LLMError):
        llm.generate("hello", model=llm.DEFAULT_MODEL)


def test_models_dict_has_haiku_default():
    assert llm.DEFAULT_MODEL == "claude-haiku-4-5"
    assert llm.DEFAULT_MODEL in llm.MODELS.values()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_llm.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'core.llm'`.

- [ ] **Step 3: Write the implementation**

Create `core/llm.py`:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_llm.py -v`
Expected: 5 passed.

Note: `load_dotenv()` reads `.env` if present but `monkeypatch.delenv` still controls what the tests see, since `get_api_key` reads `os.environ` at call time.

- [ ] **Step 5: Run the full suite**

Run: `python -m pytest -v`
Expected: all tests pass (21 total).

- [ ] **Step 6: Commit**

```bash
git add core/llm.py tests/test_llm.py
git commit -m "feat: Anthropic API wrapper with friendly error handling"
```

---

### Task 6: Streamlit app (`app.py`)

**Files:**
- Create: `app.py`

No unit tests for the UI layer — it is verified manually in Task 9.

- [ ] **Step 1: Write `app.py`**

```python
"""QA Copilot — AI assistant for manual QA work.

Run with: streamlit run app.py
"""

import streamlit as st

from core import llm
from core.export import markdown_table_to_csv
from core.prompts import render_prompt

st.set_page_config(page_title="QA Copilot", page_icon="🧪", layout="wide")

# ---------- Sidebar: settings ----------
with st.sidebar:
    st.title("🧪 QA Copilot")
    st.caption("AI assistant for user story analysis, test design and bug reporting.")

    language = st.selectbox("Output language", ["Spanish", "English"])
    detail_level = st.selectbox(
        "Detail level",
        ["junior", "senior"],
        help="junior = explains the reasoning · senior = concise, artifacts only",
    )
    model_label = st.selectbox("Model", list(llm.MODELS.keys()))
    model = llm.MODELS[model_label]

    if llm.get_api_key() is None:
        st.warning(
            "**No API key configured.**\n\n"
            "1. Create a key at [console.anthropic.com](https://console.anthropic.com)\n"
            "2. Copy `.env.example` to `.env`\n"
            "3. Paste your key there and restart the app"
        )

# ---------- Helpers ----------

def run_generation(state_key: str, prompt_name: str, user_input: str) -> None:
    """Call the API and store the result (or error) in session state."""
    prompt = render_prompt(
        prompt_name, input=user_input, language=language, detail_level=detail_level
    )
    try:
        with st.spinner("Generating..."):
            st.session_state[state_key] = llm.generate(prompt, model=model)
        st.session_state.pop(state_key + "_error", None)
    except llm.LLMError as exc:
        st.session_state[state_key + "_error"] = str(exc)
        st.session_state.pop(state_key, None)


def show_result(state_key: str, download_name: str, with_csv: bool = False) -> None:
    """Render the stored result with download buttons, or the stored error."""
    error = st.session_state.get(state_key + "_error")
    if error:
        st.error(error)
        return
    result = st.session_state.get(state_key)
    if not result:
        return
    st.markdown(result)
    st.divider()
    col1, col2 = st.columns(2)
    col1.download_button(
        "⬇️ Download Markdown", result, file_name=f"{download_name}.md",
        key=state_key + "_md",
    )
    if with_csv:
        csv_text = markdown_table_to_csv(result)
        if csv_text:
            col2.download_button(
                "⬇️ Download CSV (test case table)", csv_text,
                file_name=f"{download_name}.csv", key=state_key + "_csv",
            )


# ---------- Main layout ----------
tab_analysis, tab_gaps, tab_tests, tab_bug = st.tabs(
    ["📋 Story Analysis", "🔍 Gap Finder", "✅ Test Cases", "🐞 Bug Report"]
)

STORY_HINT = (
    "As a registered user, I want to reset my password via email, "
    "so that I can regain access to my account."
)

with tab_analysis:
    st.subheader("Analyze a user story")
    story = st.text_area("User story", key="story_analysis", height=180, placeholder=STORY_HINT)
    if st.button("Analyze story", type="primary", disabled=not story.strip()):
        run_generation("result_analysis", "analyze_story", story)
    show_result("result_analysis", "story_analysis")

with tab_gaps:
    st.subheader("Find gaps in a user story")
    story = st.text_area("User story", key="story_gaps", height=180, placeholder=STORY_HINT)
    if st.button("Find gaps", type="primary", disabled=not story.strip()):
        run_generation("result_gaps", "find_gaps", story)
    show_result("result_gaps", "gap_analysis")

with tab_tests:
    st.subheader("Generate test cases from a user story")
    story = st.text_area("User story", key="story_tests", height=180, placeholder=STORY_HINT)
    if st.button("Generate test cases", type="primary", disabled=not story.strip()):
        run_generation("result_tests", "test_cases", story)
    show_result("result_tests", "test_cases", with_csv=True)

with tab_bug:
    st.subheader("Write a bug report from an informal description")
    bug = st.text_area(
        "Describe the problem in your own words",
        key="bug_input", height=180,
        placeholder="When I leave the name field empty and press Save, nothing happens — no error, no save.",
    )
    if st.button("Write bug report", type="primary", disabled=not bug.strip()):
        run_generation("result_bug", "bug_report", bug)
    show_result("result_bug", "bug_report")
```

- [ ] **Step 2: Smoke-check that it launches**

Run: `streamlit run app.py --server.headless true` (stop it after confirming startup)
Expected: prints a local URL and no Python traceback. Without an API key the sidebar shows the setup warning — that is correct behavior.

- [ ] **Step 3: Commit**

```bash
git add app.py
git commit -m "feat: Streamlit UI with four QA tools and downloads"
```

---

### Task 7: Example stories

**Files:**
- Create: `examples/story_login.md`
- Create: `examples/story_cart.md`
- Create: `examples/outputs/README.md`

- [ ] **Step 1: Create `examples/story_login.md`**

```markdown
# Example user story — password reset

As a registered user,
I want to reset my password via a link sent to my email,
so that I can regain access to my account when I forget my password.

## Acceptance criteria

- The "Forgot password?" link is visible on the login screen.
- After submitting a registered email, the user receives a reset link.
- The reset link expires after 24 hours.
- The new password must be at least 8 characters long.
```

- [ ] **Step 2: Create `examples/story_cart.md`**

```markdown
# Example user story — shopping cart (intentionally weak)

As a user, I want to add products to my cart so I can buy them later.

Note: this story is intentionally vague — use it to demo the Gap Finder.
```

- [ ] **Step 3: Create `examples/outputs/README.md`**

```markdown
# Pre-generated outputs

This folder holds real outputs generated with QA Copilot for the stories in
`examples/`. They serve two purposes:

1. Show the quality of the results directly on GitHub.
2. Act as a backup for live demos (no internet or API needed).

Each file is named `<story>_<tool>.md`, e.g. `story_login_test_cases.md`.
```

- [ ] **Step 4: Commit**

```bash
git add examples/
git commit -m "docs: example user stories and outputs folder"
```

---

### Task 8: README with roadmap

**Files:**
- Create: `README.md`

- [ ] **Step 1: Write `README.md`**

````markdown
# 🧪 QA Copilot

An AI-powered assistant for manual QA work. Paste a user story and get a
professional analysis, gap detection and test cases; describe a defect
informally and get a ready-to-file bug report.

Built with Python, [Streamlit](https://streamlit.io) and the
[Anthropic API](https://docs.anthropic.com).

## Features

| Tool | Input | Output |
|---|---|---|
| 📋 Story Analysis | User story | Summary, acceptance criteria, INVEST assessment, testability verdict |
| 🔍 Gap Finder | User story | Ambiguities, missing criteria, edge cases, questions for the PO |
| ✅ Test Cases | User story | Gherkin scenarios + classic test case table (downloadable as CSV) |
| 🐞 Bug Report | Informal defect description | Professional bug report with severity, priority and repro steps |

Every tool supports **Spanish or English output** and two detail levels:
**junior** (explains the reasoning — great for learning) and **senior**
(concise, artifacts only).

## How it works

The prompts that power each tool live as plain Markdown files in
[`prompts/`](prompts/) — the repo doubles as a QA prompt library you can read,
reuse or adapt. The app fills in your input, sends it to Claude and renders
the result.

## Setup

Requirements: Python 3.11+ and an Anthropic API key
([create one here](https://console.anthropic.com) — a full analysis costs
about $0.01-0.02 with the default model).

```bash
git clone https://github.com/<your-user>/qa-copilot.git
cd qa-copilot
pip install -r requirements.txt
copy .env.example .env    # on Linux/macOS: cp .env.example .env
# paste your API key into .env
streamlit run app.py
```

The app opens at `http://localhost:8501`.

## Try it without an API key

The [`examples/`](examples/) folder contains sample user stories and real
pre-generated outputs, so you can see the result quality directly on GitHub.

## Running the tests

```bash
python -m pytest
```

## Roadmap

- **Phase 2 — Accounts & history:** simple login, SQLite storage of every
  analysis, and a history browser.
- **Phase 3 — Jira / Azure DevOps integration:** create generated bug reports
  as Jira issues in one click, plus a management dashboard with metrics pulled
  from Jira/Azure (bugs found vs. fixed per sprint, test cases per story).

## License

MIT
````

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: README with setup, usage and roadmap"
```

---

### Task 9: Verification & example outputs

- [ ] **Step 1: Full test suite**

Run: `python -m pytest -v`
Expected: all tests pass.

- [ ] **Step 2: Manual verification of the app**

Launch the app (`streamlit run app.py` or via the browser preview) and verify:
- All four tabs render; buttons are disabled while input is empty.
- Without an API key: sidebar shows the setup warning; pressing a button with text shows the friendly "No API key found" error (not a traceback).
- With an API key (once available): each tool returns formatted Markdown; the Test Cases tab offers both Markdown and CSV downloads; switching language to English changes the output language.

- [ ] **Step 3: Generate example outputs (requires API key — skip if not yet available)**

With `.env` configured, run this once from the repo root:

```python
# scratch script — do not commit; run with: python generate_examples.py
from pathlib import Path
from core.llm import generate, DEFAULT_MODEL
from core.prompts import render_prompt

stories = {
    "story_login": Path("examples/story_login.md").read_text(encoding="utf-8"),
    "story_cart": Path("examples/story_cart.md").read_text(encoding="utf-8"),
}
tools = ["analyze_story", "find_gaps", "test_cases"]
for story_name, story in stories.items():
    for tool in tools:
        prompt = render_prompt(tool, input=story, language="Spanish", detail_level="junior")
        out = generate(prompt, model=DEFAULT_MODEL)
        Path(f"examples/outputs/{story_name}_{tool}.md").write_text(out, encoding="utf-8")
        print("wrote", story_name, tool)
```

Then delete the scratch script and commit:

```bash
git add examples/outputs/
git commit -m "docs: pre-generated example outputs"
```

- [ ] **Step 4: Final check**

Run: `git status`
Expected: clean working tree; `.env` (if present) is ignored, never staged.

---

## Deferred to a later session (not part of this plan)

- Screenshots for the README (taken once the app runs with a real key).
- Creating the GitHub account + repo and pushing (`gh auth login`, `gh repo create qa-copilot --public --source . --push`).
- Phases 2 and 3 (login/history, Jira/Azure integration).
