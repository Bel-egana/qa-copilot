# QA Copilot — Phase 1 Design

**Date:** 2026-07-14
**Status:** Approved for implementation
**Author:** Bel (with Claude)

## Purpose

QA Copilot is an AI-powered assistant for manual QA work. Given a user story or an informal bug description, it produces professional QA artifacts: story analysis, gap/ambiguity detection, test cases, and bug reports.

Primary goal: a polished, demonstrable portfolio project for QA Manual/Analyst job interviews. It must be easy to run live (one command), look professional on GitHub, and showcase QA judgment above all.

## Scope — Phase 1

A local Streamlit web app backed by the Anthropic API. No login, no database, no external integrations (those are Phase 2/3 — see Roadmap).

### Features

The app has two input modes and four outputs, organized as tabs:

**Input A: User story** (free text, pasted by the user)

1. **Story Analysis** — summary of the story, detected/extracted acceptance criteria, quality assessment against INVEST criteria, and a testability verdict.
2. **Gap Finder** — ambiguities, missing acceptance criteria, uncovered edge cases, and a list of questions a QA should ask the Product Owner before testing.
3. **Test Cases** — test cases derived from the story in two formats:
   - Gherkin (Given/When/Then)
   - Classic table: ID, title, preconditions, steps, expected result, priority
   - Coverage must include happy path, negative cases, and edge cases.

**Input B: Informal bug description** (free text, e.g. "the save button does nothing when the name field is empty")

4. **Bug Report** — a professional bug report: title, severity, priority, environment placeholder, steps to reproduce, actual result, expected result, additional notes.

### Controls

- **Output language:** Spanish / English (selectbox; UI chrome stays in English).
- **Detail level:** Junior (more explanatory, includes reasoning) / Senior (concise, artifacts only).
- **Model:** Claude Haiku 4.5 (default, cheapest) / Claude Sonnet (selectbox).
- **Download** buttons: results as Markdown; test-case table also as CSV.

## Architecture

```
qa-copilot/
├── README.md              # screenshots, setup, usage, roadmap
├── app.py                 # Streamlit UI (thin: layout + calls into core)
├── core/
│   ├── llm.py             # Anthropic API client wrapper
│   └── prompts.py         # loads prompt files, fills placeholders
├── prompts/               # the prompt library (plain .md, visible in repo)
│   ├── analyze_story.md
│   ├── find_gaps.md
│   ├── test_cases.md
│   └── bug_report.md
├── examples/              # sample user stories + pre-generated outputs
│   ├── story_login.md
│   ├── story_cart.md
│   └── outputs/           # committed real outputs (demo fallback, no API needed)
├── tests/                 # pytest: prompt loading, placeholder filling, CSV export
├── requirements.txt
├── .env.example           # ANTHROPIC_API_KEY=your-key-here
└── .gitignore             # .env, __pycache__, etc.
```

### Data flow

1. User pastes text, picks language/detail/model, clicks the action button.
2. `prompts.py` loads the matching `prompts/*.md` template and fills placeholders: `{input}`, `{language}`, `{detail_level}`.
3. `llm.py` sends it to the Anthropic Messages API and returns the text.
4. `app.py` renders the Markdown result and offers downloads.

Prompts live in plain Markdown files so the repo doubles as a readable prompt library — a talking point in interviews ("here is exactly how I instruct the model").

### Key decisions

- **Streamlit** over Flask/CLI: one-command demo (`streamlit run app.py`), professional look with minimal code, standard for AI demos.
- **Haiku 4.5 default:** ~$0.01–0.02 per full analysis; $5 of credit covers hundreds of runs.
- **API key via `.env`** (python-dotenv), never committed; `.env.example` documents it. If the key is missing, the app shows a friendly setup hint instead of crashing.
- **`examples/outputs/` committed to the repo:** serves as demo fallback if the interview has no internet/credit, and shows result quality directly on GitHub.
- **Repo language:** English (README, code, prompts). Generated output is bilingual via the language selector.

## Error handling

- Missing/invalid API key → clear on-screen instructions (create key, put it in `.env`).
- API errors (rate limit, network) → human-readable error banner, never a stack trace.
- Empty input → button disabled or gentle validation message.

## Testing

- `pytest` unit tests for the non-LLM parts: prompt file loading, placeholder substitution, CSV conversion of test-case tables.
- LLM output quality is validated manually via the committed examples (no automated evals in Phase 1).

## Out of scope (Phase 1)

Login, database, history, Jira/Azure integration, management dashboard, automated prompt evals, deployment/hosting.

## Roadmap (documented in README)

- **Phase 2 — Accounts & history:** simple login (pre-created users), SQLite storage of every analysis (who, when, input, output), a history browser.
- **Phase 3 — Jira/Azure DevOps integration & management dashboard:**
  - Push: create a generated bug report as a Jira issue / Azure work item in one click.
  - Pull: metrics dashboard reading from Jira/Azure — bugs found vs. fixed per sprint, test cases written per user story, trends.
  - Free tiers of Jira Cloud / Azure DevOps make a live demo possible at no cost.

## Success criteria

- `streamlit run app.py` works on a fresh clone after `pip install -r requirements.txt` + `.env` setup.
- All four features produce professional-quality output in both languages.
- README lets a stranger (junior or senior) install and use it without help.
- Public GitHub repo with screenshots, examples, and clean commit history.
