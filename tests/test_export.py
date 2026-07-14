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
