from collections.abc import Iterator
from pathlib import Path

from .pdf_layout import PageLayout

SEPARATOR = "----------xxx\n\n"
temp_file = Path(__file__).parent.parent / "temp" / "temp.txt"


def set_file(lines: Iterator[dict], p: Path = temp_file) -> Path:
    """Using contextualized lines, create a text file based on
    PageLayout sections.

    Args:
        lines (Iterator[dict]): _description_
        p (Path, optional): _description_. Defaults to temp_file.

    Returns:
        Path: _description_
    """
    decision_type = None
    date_found = None
    annex_texts = []
    decision_texts = []
    for line in lines:
        if layout := line.get("layout"):
            if layout == PageLayout.Header:
                if decision_type is None and line.get("decision_type"):
                    decision_type = line["decision_type"]
                if date_found is None and line.get("date_found"):
                    date_found = line["date_found"]

            if layout == PageLayout.Body:
                decision_texts.append(line.get("text"))

            if layout == PageLayout.Annex:
                annex_texts.append(line.get("text"))

    with open(p, "w+") as target:
        target.write(f"Type: {decision_type}\n")
        if date_found:
            target.write(f"Date: {date_found}\n")
        target.write(SEPARATOR)
        target.write("\n\n".join(decision_texts))
        target.write(SEPARATOR)
        target.write("\n\n".join(annex_texts))
    return p
