# QA Copilot Phase 2 (History) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Auto-save every generation to SQLite and add a History tab to browse, re-download, and delete past analyses.

**Architecture:** New `core/history.py` owns all DB access (parameterized queries only, temp-path injectable for tests). `app.py` saves after each successful generation and gains a fifth tab. No new dependencies (stdlib `sqlite3`).

**Tech Stack:** Python stdlib `sqlite3`, Streamlit, pytest.

**Working directory:** `D:\qa-copilot`. Spec: `docs/specs/2026-07-14-qa-copilot-phase2-history-design.md`.

---

### Task 1: `core/history.py` — TDD

**Files:**
- Create: `core/history.py`
- Test: `tests/test_history.py`
- Modify: `.gitignore` (add `data/`)

- [ ] **Step 1: Write the failing tests**

Create `tests/test_history.py`:

```python
from core import history


def _db(tmp_path):
    return tmp_path / "test.db"


def test_save_returns_id_and_list_returns_row(tmp_path):
    db = _db(tmp_path)
    row_id = history.save_analysis(
        "analyze_story", "my story", "the output", "Spanish", "junior",
        "gemini-3.5-flash", db_path=db,
    )
    assert isinstance(row_id, int)

    rows = history.list_analyses(db_path=db)
    assert len(rows) == 1
    row = rows[0]
    assert row["id"] == row_id
    assert row["tool"] == "analyze_story"
    assert row["input"] == "my story"
    assert row["output"] == "the output"
    assert row["language"] == "Spanish"
    assert row["detail_level"] == "junior"
    assert row["model"] == "gemini-3.5-flash"
    assert row["created_at"]  # non-empty timestamp


def test_list_newest_first(tmp_path):
    db = _db(tmp_path)
    first = history.save_analysis("find_gaps", "a", "1", "English", "senior", "m", db_path=db)
    second = history.save_analysis("find_gaps", "b", "2", "English", "senior", "m", db_path=db)
    ids = [r["id"] for r in history.list_analyses(db_path=db)]
    assert ids == [second, first]


def test_filter_by_tool(tmp_path):
    db = _db(tmp_path)
    history.save_analysis("analyze_story", "a", "1", "English", "senior", "m", db_path=db)
    history.save_analysis("bug_report", "b", "2", "English", "senior", "m", db_path=db)
    rows = history.list_analyses(tool="bug_report", db_path=db)
    assert len(rows) == 1
    assert rows[0]["tool"] == "bug_report"


def test_delete_removes_only_target(tmp_path):
    db = _db(tmp_path)
    keep = history.save_analysis("test_cases", "keep", "1", "English", "senior", "m", db_path=db)
    kill = history.save_analysis("test_cases", "kill", "2", "English", "senior", "m", db_path=db)
    history.delete_analysis(kill, db_path=db)
    ids = [r["id"] for r in history.list_analyses(db_path=db)]
    assert ids == [keep]


def test_delete_missing_id_is_noop(tmp_path):
    db = _db(tmp_path)
    history.save_analysis("test_cases", "a", "1", "English", "senior", "m", db_path=db)
    history.delete_analysis(99999, db_path=db)  # must not raise
    assert len(history.list_analyses(db_path=db)) == 1


def test_sql_injection_input_is_stored_verbatim(tmp_path):
    db = _db(tmp_path)
    evil = "'; DROP TABLE analyses; --"
    history.save_analysis(evil, evil, evil, evil, evil, evil, db_path=db)

    rows = history.list_analyses(db_path=db)
    assert rows[0]["input"] == evil  # stored as data, not executed

    # Table survived: another save still works
    history.save_analysis("analyze_story", "after", "ok", "English", "senior", "m", db_path=db)
    assert len(history.list_analyses(db_path=db)) == 2

    # Filtering by the evil string is also safe
    assert len(history.list_analyses(tool=evil, db_path=db)) == 1
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_history.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'core.history'`.

- [ ] **Step 3: Write the implementation**

Create `core/history.py`:

```python
"""SQLite persistence for generated analyses.

All queries are parameterized — user text never reaches the SQL string.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "qa_copilot.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tool TEXT NOT NULL,
    input TEXT NOT NULL,
    output TEXT NOT NULL,
    language TEXT NOT NULL,
    detail_level TEXT NOT NULL,
    model TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
)
"""


def _connect(db_path: Path) -> sqlite3.Connection:
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute(_SCHEMA)
    return conn


def init_db(db_path: Path = DB_PATH) -> None:
    _connect(db_path).close()


def save_analysis(
    tool: str,
    input_text: str,
    output: str,
    language: str,
    detail_level: str,
    model: str,
    db_path: Path = DB_PATH,
) -> int:
    conn = _connect(db_path)
    try:
        with conn:
            cursor = conn.execute(
                "INSERT INTO analyses (tool, input, output, language, detail_level, model) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (tool, input_text, output, language, detail_level, model),
            )
            return cursor.lastrowid
    finally:
        conn.close()


def list_analyses(tool: str | None = None, db_path: Path = DB_PATH) -> list[dict]:
    conn = _connect(db_path)
    try:
        if tool is None:
            rows = conn.execute("SELECT * FROM analyses ORDER BY id DESC").fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM analyses WHERE tool = ? ORDER BY id DESC", (tool,)
            ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def delete_analysis(analysis_id: int, db_path: Path = DB_PATH) -> None:
    conn = _connect(db_path)
    try:
        with conn:
            conn.execute("DELETE FROM analyses WHERE id = ?", (analysis_id,))
    finally:
        conn.close()
```

- [ ] **Step 4: Add `data/` to `.gitignore`**

Append under the "Secrets" block:

```gitignore
# Local database
data/
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python -m pytest tests/test_history.py -v`
Expected: 6 passed.

- [ ] **Step 6: Commit**

```bash
git add core/history.py tests/test_history.py .gitignore
git commit -m "feat: SQLite analysis history with parameterized queries"
```

---

### Task 2: App integration — auto-save + History tab

**Files:**
- Modify: `app.py`

- [ ] **Step 1: Import and save after generation**

Add to the imports in `app.py`:

```python
from core.history import delete_analysis, list_analyses, save_analysis
```

In `run_generation()`, after the successful generate (inside the `try`, after
`st.session_state[state_key] = ...` and the `pop`), add:

```python
        try:
            save_analysis(
                prompt_name, user_input, st.session_state[state_key],
                language, detail_level, model,
            )
        except Exception:
            st.warning("The result could not be saved to history (it is still shown below).")
```

- [ ] **Step 2: Add the History tab**

Change the tabs line to:

```python
tab_analysis, tab_gaps, tab_tests, tab_bug, tab_history = st.tabs(
    ["📋 Story Analysis", "🔍 Gap Finder", "✅ Test Cases", "🐞 Bug Report", "📚 History"]
)
```

Append at the end of the file:

```python
TOOL_LABELS = {
    "analyze_story": "📋 Story Analysis",
    "find_gaps": "🔍 Gap Finder",
    "test_cases": "✅ Test Cases",
    "bug_report": "🐞 Bug Report",
}

with tab_history:
    st.subheader("Saved analyses")
    filter_label = st.selectbox("Filter by tool", ["All"] + list(TOOL_LABELS.values()))
    tool_filter = next(
        (key for key, label in TOOL_LABELS.items() if label == filter_label), None
    )

    entries = list_analyses(tool=tool_filter)
    if not entries:
        st.info("Nothing here yet — every analysis you generate is saved automatically.")
    for entry in entries:
        snippet = entry["input"][:70].replace("\n", " ")
        title = f"{entry['created_at']} · {TOOL_LABELS[entry['tool']]} · {snippet}"
        with st.expander(title):
            st.caption(
                f"{entry['language']} · {entry['detail_level']} · {entry['model']}"
            )
            st.markdown("**Input**")
            st.text(entry["input"])
            st.markdown("**Result**")
            st.markdown(entry["output"])
            st.divider()
            col1, col2, col3 = st.columns(3)
            col1.download_button(
                "⬇️ Markdown", entry["output"],
                file_name=f"{entry['tool']}_{entry['id']}.md",
                key=f"hist_md_{entry['id']}",
            )
            if entry["tool"] == "test_cases":
                csv_text = markdown_table_to_csv(entry["output"])
                if csv_text:
                    col2.download_button(
                        "⬇️ CSV", csv_text,
                        file_name=f"test_cases_{entry['id']}.csv",
                        key=f"hist_csv_{entry['id']}",
                    )
            if col3.button("🗑️ Delete", key=f"hist_del_{entry['id']}"):
                delete_analysis(entry["id"])
                st.rerun()
```

- [ ] **Step 3: Verify the app still runs**

Run: `streamlit run app.py --server.headless true` — no traceback; History tab
shows the empty state.

- [ ] **Step 4: Commit**

```bash
git add app.py
git commit -m "feat: auto-save generations and History tab"
```

---

### Task 3: README update

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Add History to the features table**

Add this row at the end of the features table:

```markdown
| 📚 History | — | Every analysis is auto-saved locally (SQLite); browse, re-download or delete past results |
```

- [ ] **Step 2: Update the roadmap**

Replace the Phase 2 roadmap bullet with:

```markdown
- ~~**Phase 2 — Analysis history:**~~ ✅ shipped — SQLite auto-save + History tab.
- **Authentication:** deliberately deferred — the app is local and
  single-user; login/roles become relevant only if it is deployed multi-user.
```

Keep the Phase 3 bullet unchanged.

- [ ] **Step 3: Commit and push**

```bash
git add README.md
git commit -m "docs: README — history feature and roadmap update"
git push origin master
```

---

### Task 4: Verification

- [ ] **Step 1: Full suite** — `python -m pytest -v` → all pass (27 total).
- [ ] **Step 2: Live check** — generate one analysis in the running app, open the History tab, confirm the entry appears; delete it; confirm empty state. Confirm `git status` never shows `data/`.
- [ ] **Step 3: Push** — working tree clean, everything pushed.
