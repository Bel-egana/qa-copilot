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
