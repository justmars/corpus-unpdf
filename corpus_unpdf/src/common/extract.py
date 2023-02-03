import re
from typing import NamedTuple, Self

from pdfplumber.page import CroppedPage

line_break = re.compile(r"\s*\n+\s*")

paragraph_break = re.compile(r"\s{10,}(?=[A-Z])")

footnote_nums = re.compile(r"\n\s+(?P<fn>\d+)(?=\s+[A-Z])")


class Bodyline(NamedTuple):
    num: int
    line: str

    @classmethod
    def extract_lines(cls, text: str) -> list[Self]:
        """Get paragraphs using regex `\\s{10,}(?=[A-Z])`
        implying many spaces before a capital letter then
        remove new lines contained in non-paragraph lines.

        Args:
            text (str): Presumes pdfplumber.extract_text

        Returns:
            list[Self]: Bodylines of segmented text
        """
        lines = []
        for num, par in enumerate(paragraph_break.split(text), start=1):
            obj = cls(num=num, line=line_break.sub(" ", par).strip())
            lines.append(obj)
        lines.sort(key=lambda obj: obj.num)
        return lines

    @classmethod
    def from_cropped(cls, crop: CroppedPage) -> list[Self]:
        return cls.extract_lines(
            crop.extract_text(layout=True, keep_blank_chars=True)
        )


class Footnote(NamedTuple):
    fn_id: int
    note: str

    @classmethod
    def extract_notes(cls, text: str) -> list[Self]:
        """Get footnote digits using regex `\\n\\s+(?P<fn>\\d+)(?=\\s+[A-Z])`
        then for each matching span, the start span becomes the anchor
        for the balance of the text for each remaining foornote in the while
        loop. The while loop extraction must use `.pop()` where the last
        item is removed first.

        Args:
            text (str): Presumes pdfplumber.extract_text

        Returns:
            list[Self]: Footnotes separated by digits.
        """
        notes = []
        while True:
            matches = list(footnote_nums.finditer(text))
            if not matches:
                break
            note = matches.pop()  # start from the last
            footnote_num = int(note.group("fn"))
            digit_start, digit_end = note.span()
            footnote_body = text[digit_end:].strip()
            obj = cls(fn_id=footnote_num, note=footnote_body)
            notes.append(obj)
            text = text[:digit_start]
        notes.sort(key=lambda obj: obj.fn_id)
        return notes

    @classmethod
    def from_cropped(cls, crop: CroppedPage) -> list[Self]:
        return cls.extract_notes(
            crop.extract_text(layout=True, keep_blank_chars=True)
        )
