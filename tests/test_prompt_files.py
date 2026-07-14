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
