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
