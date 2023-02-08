import re
from dataclasses import dataclass, field
from typing import NamedTuple, Self

import cv2
import numpy
import pytesseract
from pdfplumber.page import CroppedPage, Page

from .common import PageCut, get_img_from_page
from .content_markers import CourtCompositionChoices, DecisionCategoryChoices
from .page_footer import get_page_end
from .page_header import get_header_line, get_page_num

line_break = re.compile(r"\s*\n+\s*")

paragraph_break = re.compile(r"\s{10,}(?=[A-Z])")

footnote_nums = re.compile(r"\n\s+(?P<fn>\d+)(?=\s+[A-Z])")


class Bodyline(NamedTuple):
    """Each page may be divided into lines which, for our purposes,
    will refer to an arbitrary segmentation of text based on regex parameters.

    Field | Type | Description
    --:|:--:|:--
    `num` | int | Order in the page
    `line` | str | The text found based on segmentation
    """

    page_num: int
    order_num: int
    line: str

    @classmethod
    def split(cls, prelim_lines: list[str], page_num: int) -> list[Self]:
        """Get paragraphs using regex `\\s{10,}(?=[A-Z])`
        implying many spaces before a capital letter then
        remove new lines contained in non-paragraph lines.

        Args:
            prelim_lines (list[str]): Previously split text

        Returns:
            list[Self]: Bodylines of segmented text
        """
        lines = []
        for order_num, par in enumerate(prelim_lines, start=1):
            obj = cls(
                page_num=page_num,
                order_num=order_num,
                line=line_break.sub(" ", par).strip(),
            )
            lines.append(obj)
        lines.sort(key=lambda obj: obj.order_num)
        return lines


class Footnote(NamedTuple):
    """Each page may contain an annex which consists of footnotes. Note
    that this is based on a imperfect use of regex to detect the footnote
    number `fn_id` and its corresponding text `note`.

    Field | Type | Description
    --:|:--:|:--
    `fn_id` | int | Footnote number
    `note` | str | The text found based on segmentation of footnotes
    """

    page_num: int
    fn_id: int
    note: str

    @classmethod
    def extract_notes(cls, text: str, page_num: int) -> list[Self]:
        """Get footnote digits using regex `\\n\\s+(?P<fn>\\d+)(?=\\s+[A-Z])`
        then for each matching span, the start span becomes the anchor
        for the balance of the text for each remaining foornote in the while
        loop. The while loop extraction must use `.pop()` where the last
        item is removed first.

        Args:
            text (str): Text that should be convertible to footnotes based on regex

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
            obj = cls(
                page_num=page_num,
                fn_id=footnote_num,
                note=footnote_body,
            )
            notes.append(obj)
            text = text[:digit_start]
        notes.sort(key=lambda obj: obj.fn_id)
        return notes


@dataclass
class DecisionPage:
    """Metadata of a single decision page.

    Field | Description
    --:|:--
    `page_num` | The page number of the Decision page
    `body` | The main content above the annex, if existing
    `segments` | Segments of the `body`'s text in the given `page_num`, see [Bodyline][bodyline]
    `annex` | Portion of page containing the footnotes; some pages are annex-free
    `footnotes` | Each footnote item in the `annex`'s text in the given `page_num`, see [Footnote][footnote]
    """  # noqa: E501

    page_num: int
    body: CroppedPage
    body_text: str
    annex: CroppedPage | None = None
    annex_text: str | None = None
    segments: list[Bodyline] = field(default_factory=list)
    footnotes: list[Footnote] = field(default_factory=list)

    def __post_init__(self):
        alpha = paragraph_break.split(self.body_text)
        beta = self.body_text.split("\n\n")
        candidates = alpha or beta
        self.segments = Bodyline.split(candidates, self.page_num)
        if self.annex and self.annex_text:
            self.footnotes = Footnote.extract_notes(
                self.annex_text, self.page_num
            )

    @classmethod
    def set(
        cls,
        page: Page,
        start_y: float | int | None = None,
        end_y: float | int | None = None,
    ) -> Self:
        """
        A `header_line` (related to `start_y`) and `page_line` (related to `end_y`)
        are utilized as local variables in this function.

        The `header_line` is the imaginary line at the top of the page.
        If the `start_y` is supplied, it means that the `header_line`
        no longer needs to be calculated.

        The `page_line` is the imaginary line at the bottom of the page.
        If the `end_y` is supplied, it means that the calculated `page_line`
        ought to be replaced.

        The presence of a `header_line` and a `page_endline` determine
        what to extract from a given `page`.

        Args:
            page (Page): The pdfplumber page to evaluate
            start_y (float | int | None, optional): If present, refers to
                The y-axis point of the starter page. Defaults to None.
            end_y (float | int | None, optional): If present, refers to
                The y-axis point of the ender page. Defaults to None.

        Returns:
            Self: Page with individual components mapped out.
        """
        im = get_img_from_page(page)

        header_line = start_y or get_header_line(im, page)
        if not header_line:
            raise Exception(f"No header line in {page.page_number=}")

        end_of_content, e = get_page_end(im, page)
        page_line = end_y or end_of_content

        body = PageCut.set(page=page, y0=header_line, y1=page_line)
        body_text = cls.get_content(body)
        annex = None
        annex_text = None
        if e:
            annex = PageCut.set(page=page, y0=end_of_content, y1=e)
            annex_text = cls.get_content(annex)

        return cls(
            page_num=get_page_num(page, header_line),
            body=body,
            body_text=body_text,
            annex=annex,
            annex_text=annex_text,
        )

    @classmethod
    def get_content(cls, crop: CroppedPage):
        return cls.text_from_plumber(crop) or cls.text_from_image(crop)

    @classmethod
    def text_from_plumber(cls, crop: CroppedPage) -> str:
        """pdfplumber features an experimental setting of capturing the
        image's blank spaces and layout. This would be useful in determining
        line breaks.

        Args:
            crop (CroppedPage): pdfplumber CroppedPage.

        Returns:
            str: text found from the cropped page.
        """
        return crop.extract_text(layout=True, keep_blank_chars=True).strip()

    @classmethod
    def text_from_image(cls, crop: CroppedPage) -> str:
        """In the event that pdfplumber's `extract_text()` fails, i.e. no
        text is produced, use the pytesseract method. First convert the
        image to its `PIL` format then from convert it to openCV
        so that it can be used by pytesseract."""
        return pytesseract.image_to_string(
            cv2.cvtColor(
                numpy.array(crop.to_image(resolution=300).original),
                cv2.COLOR_RGB2BGR,
            )
        ).strip()


@dataclass
class Opinion:
    """Metadata of a pdf file parsed via `get_opinion()`

    Field | Description
    --:|:--
    `label` | How the opinion is labelled
    `writer` | When available, the writer of the case
    `pages` | A list of [Decision Pages][decision-pages]
    `body` | The compiled string consisting of each page's `body_text`
    `annex` | The compiled string consisting of each page's `annex_text`, if existing
    `segments` | Each [bodyline][bodyline] of the body's text
    `footnotes` | Each [footnote][footnote] in the annex's text
    """

    label: str
    writer: str
    pages: list[DecisionPage] = field(default_factory=list)
    segments: list[Bodyline] = field(default_factory=list)
    footnotes: list[Footnote] = field(default_factory=list)
    body: str = ""
    annex: str = ""

    def __repr__(self) -> str:
        return (
            f"{self.writer.title()} | {self.label.title()}: pages"
            f" {len(self.pages)}"
        )


@dataclass
class Decision:
    """Metadata of a pdf file parsed via `get_decision()`

    Field | Description
    --:|:--
    `composition` | The composition of the Supreme Court that decided the case
    `category` | When available, whether the case is a "Decision" or a "Resolution"
    `header` | The top portion of the page, usually excluded from metadata
    `writer` | When available, the writer of the case
    `notice` | When True, means that there is no `category` available
    `pages` | A list of [Decision Pages][decision-pages]
    `body` | The compiled string consisting of each page's `body_text`
    `annex` | The compiled string consisting of each page's `annex_text`, if existing
    `segments` | Each [bodyline][bodyline] of the body's text
    `footnotes` | Each [footnote][footnote] in the annex's text
    """

    composition: CourtCompositionChoices
    category: DecisionCategoryChoices | None = None
    header: CroppedPage | None = None
    writer: str | None = None
    notice: bool = False
    pages: list[DecisionPage] = field(default_factory=list)
    segments: list[Bodyline] = field(default_factory=list)
    footnotes: list[Footnote] = field(default_factory=list)
    body: str = ""
    annex: str = ""

    def __repr__(self) -> str:
        return f"Decision {self.composition.value}, pages {len(self.pages)}"
