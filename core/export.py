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
