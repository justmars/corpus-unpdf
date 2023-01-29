import re
from collections.abc import Iterator
from enum import Enum
from typing import Any

from dateutil.parser import parse

# Pattern matching for get_texts
newline = re.compile(r"\n")
double_space = re.compile(r"\n\n")


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


def extract_date_citation(text: str) -> dict:
    """In a page layout's header, the full docket citation may be included
    e.g. `GR <num> <date>` but sometimes only the number is indicated, without
    the date, e.g. `GR <num>`.

    Args:
        text (str): Expects  `GR <num> <date>` or `GR <num>`

    Returns:
        dict: {"partial_docket": `<value>`, "date_found": `<value>`}
    """
    try:
        texts = text.strip().split()
        if len(texts) > 4:
            candidate = " ".join(texts[-3:])
            return {
                "partial_docket": text.removesuffix(candidate).strip(),
                "date_found": parse(candidate, fuzzy=True).date(),
            }
    except Exception:
        ...
    return {"partial_docket": text, "date_found": None}


def extract_header_meta(text: str) -> dict:
    """Given the top portion of the page, extract the metadata of the header.

    Args:
        text (str): Expects `<decision_type>` `<page_num>` `<partial docket>`

    Returns:
        dict: Either an empty dict or one containing metadata fields.
    """
    texts = text.split()
    try:
        initial = dict(decision_type=texts.pop(0))
        _ = texts.pop(0)  # should be page num
        return initial | extract_date_citation(" ".join(texts))
    except Exception:
        ...
    return {}


class PageLayout(Enum):
    """Layouting sections mapped to a Supreme Court decision:

    1. Header
    2. Body
    3. Footer
    """

    Header = "header"
    Body = "body"
    Annex = "annex"

    def get_texts(self, page_num: int, text: str) -> Iterator[dict[str, Any]]:
        """Given a section of the page, split up the page
        first by double-spaced newlines and then remove
        each newline contained within this initial split.

        Args:
            page_num (int): Page number represented by the text
            text (str): The converted text from its original image


        Yields:
            Iterator[dict[str, Any]]: Contextualized layouted line
        """
        paragraphs = double_space.split(standardize(text))
        for pos, paragraph_text in enumerate(paragraphs):
            text = newline.sub(" ", paragraph_text)
            base = {"layout": self, "page": page_num, "pos": pos, "text": text}
            if self == PageLayout.Header:
                yield base | extract_header_meta(paragraph_text)
            else:
                yield base
