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
