import re

from typing import NamedTuple
from pdfplumber.page import CroppedPage
from typing import Self

line_break = re.compile(r"\s*\n+\s*")

paragraph_break = re.compile(r"\s{12,}(?=[A-Z])")

footnote_nums = re.compile(r"\n\s+(?P<fn>\d+)(?=\s+[A-Z])")


class Bodyline(NamedTuple):
    num: int
    line: str

    @classmethod
    def extract(cls, text: str) -> list[Self]:
        lines = []
        for num, par in enumerate(paragraph_break.split(text), start=1):
            obj = cls(num=num, line=line_break.sub(" ", par).strip())
            lines.append(obj)
        lines.sort(key=lambda obj: obj.num)
        return lines

    @classmethod
    def from_cropped(cls, crop: CroppedPage) -> list[Self]:
        text = crop.extract_text(layout=True, keep_blank_chars=True)
        return cls.extract(text)


class Footnote(NamedTuple):
    fn_id: int
    note: str

    @classmethod
    def extract(cls, text: str) -> list[Self]:
        notes = []
        while True:
            matches = list(footnote_nums.finditer(text))
            if not matches:
                break
            note = matches.pop()
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
        text = crop.extract_text(layout=True, keep_blank_chars=True)
        return cls.extract(text)
