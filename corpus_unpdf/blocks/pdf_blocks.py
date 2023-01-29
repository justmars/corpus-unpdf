import re
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pdfplumber

starts_with_small_letter = re.compile(r"^[a-z]")

break_between_small_letters = re.compile(r"(?<=[a-z])\n(?=[a-z])")

space_break_letter = re.compile(r"\s\n(?=\w)")


def standardize(text: str):
    return (
        text.replace("\xa0", "")
        .replace("\xad", "-")
        .replace("“", '"')
        .replace("”", '"')
        .replace("‘", "'")
        .replace("’", "'")
        .strip()
    )


def extract_blocks(pdfpath: Path) -> Iterator[dict[str, Any]]:
    """Following an experimental layout from `pdfplumber`,
    generate contextualized blocks based on some regex patterns.

    Args:
        pdfpath (Path): _description_

    Yields:
        Iterator[dict[str, Any]]: _description_
    """
    pdf = pdfplumber.open(pdfpath)
    for counter, page in enumerate(pdf.pages):
        if counter != 0:  # assumes only first page does not need to be cropped
            page = page.crop(
                bbox=(0, 0.09 * float(page.height), page.width, page.height),
                relative=False,
                strict=True,
            )
        page_structure = page.extract_text(
            layout=True,  # experimental, follows page structure spacing
            keep_blank_chars=True,  # enables more context in spacing
        )
        content_of_page = standardize(page_structure)
        newlines_preceded_by_spaces = space_break_letter.split(content_of_page)
        for counter, line in enumerate(newlines_preceded_by_spaces):
            remove_false_breaks = break_between_small_letters.sub(" ", line)
            lines_proper = remove_false_breaks.splitlines()
            for subcounter, text in enumerate(lines_proper):
                yield {
                    "page": page.page_number,
                    "counter": counter,
                    "line": subcounter,
                    "text": text,
                }


temp_pdf = Path(__file__).parent.parent / "temp" / "temp.pdf"

"""
def extract_output(url: str, pdf: Path = temp_pdf):
    res = httpx.get(url, timeout=120)
    pdf.write_bytes(res.content)
    blocks = (f"{blk['text'].lstrip()}\n" for blk in extract_blocks(pdf))
    return "".join(blocks)
"""
