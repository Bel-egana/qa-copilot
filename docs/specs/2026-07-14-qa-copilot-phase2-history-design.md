# QA Copilot — Phase 2 Design: Analysis History

**Date:** 2026-07-14
**Status:** Approved for implementation
**Author:** Bel (with Claude)
**Builds on:** Phase 1 (`2026-07-14-qa-copilot-phase1-design.md`)

## Purpose

Persist every generation so the user can revisit, re-download, and manage past
analyses. Scope deliberately excludes login/authentication: the app is local
and single-user; auth is deferred until the app is ever deployed multi-user
(noted in the README roadmap).

## Scope — Phase 2

### Features

1. **Auto-save:** every successful generation (any of the four tools) is saved
   automatically with: tool, input text, output markdown, language, detail
   level, model, and timestamp. Failed generations are not saved.
2. **📚 History tab** (fifth tab in the app):
   - List of saved analyses, newest first, filterable by tool.
   - Each entry shows: date/time, tool, and a snippet of the input.
   - Expanding an entry shows the full input and the rendered output, with
     the same download buttons as a fresh result (Markdown; CSV for test
     cases).
   - A delete button per entry (with no confirmation dialog — single-user
     local data, and the action is scoped to one row).
   - Empty state: friendly message when there is no history yet.

### Storage

- **SQLite** via Python's stdlib `sqlite3` — no new dependencies.
- DB file: `data/qa_copilot.db`, created on first use. `data/` is gitignored.
- Single table:

```sql
CREATE TABLE IF NOT EXISTS analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tool TEXT NOT NULL,
    input TEXT NOT NULL,
    output TEXT NOT NULL,
    language TEXT NOT NULL,
    detail_level TEXT NOT NULL,
    model TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);
```

### Security requirements

- **All queries parameterized** (`?` placeholders) — no string-concatenated
  SQL, ever. A dedicated test feeds SQL-injection-style input
  (`'; DROP TABLE analyses; --`) through the public API and asserts the table
  survives and the text is stored verbatim.
- DB file never committed (gitignore `data/`).

## Architecture

```
core/
└── history.py      # all DB access: init_db, save_analysis, list_analyses,
                    # delete_analysis. Pure functions taking an optional
                    # db_path (defaults to data/qa_copilot.db) for testability.
app.py              # + History tab; run_generation() calls save_analysis()
tests/
└── test_history.py # TDD: save/list/filter/delete + SQL injection test
```

### `core/history.py` interface

```python
DB_PATH: Path                               # data/qa_copilot.db
init_db(db_path=DB_PATH) -> None            # create table if missing
save_analysis(tool, input_text, output, language, detail_level, model,
              db_path=DB_PATH) -> int       # returns new row id
list_analyses(tool=None, db_path=DB_PATH) -> list[dict]   # newest first
delete_analysis(analysis_id, db_path=DB_PATH) -> None
```

Each returned dict has keys: `id, tool, input, output, language,
detail_level, model, created_at`.

### Data flow changes

`run_generation()` in `app.py`: after a successful `llm.generate()`, call
`save_analysis(...)`. Errors while saving must not break the result display —
wrap in try/except and show a small warning instead.

## Error handling

- DB errors on save → result still shown; a non-blocking warning appears.
- Deleting an id that no longer exists → no-op, no crash.

## Testing

`pytest` on a temp-file DB (never the real one): table creation, save returns
id, list ordering (newest first), filter by tool, delete removes only the
target row, SQL-injection input stored harmlessly.

## Out of scope (Phase 2)

Login/auth (deferred until multi-user deployment), search within history,
editing saved entries, export-all, pagination (fine until hundreds of rows).

## Success criteria

- Generating in any tab silently adds a row; the History tab shows it.
- Filter, expand, re-download, and delete work.
- All tests pass, including the SQL injection test.
- `data/` never appears in `git status`.
