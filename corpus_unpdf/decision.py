from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Self

import numpy
import pdfplumber
from pdfplumber.page import CroppedPage, Page

from .src import (
    SIDE_MARGIN,
    Bodyline,
    CourtCompositionChoices,
    DecisionCategoryChoices,
    Footnote,
    PageCut,
    PositionCourtComposition,
    PositionDecisionCategoryWriter,
    PositionNotice,
    get_annex_y_axis,
    get_header_line,
    get_page_and_img,
    get_page_num,
    get_terminal_page_pos,
)


@dataclass
class DecisionPage:
    """Metadata of a single page of the pdf file parsed via `get_decision()`

    Field | Description
    --:|:--
    `page_num` | The page number of the Decision page
    `body` | The main content above the annex, if existing
    `lines` | Segments of the `body`'s text in the given `page_num`
    `annex` | Portion of page containing the footnotes; some pages are annex-free
    `footnotes` | Each footnote item in the `annex`'s text in the given `page_num`
    """

    page_num: int
    body: CroppedPage
    annex: CroppedPage | None = None
    lines: list[Bodyline] = field(default_factory=list)
    footnotes: list[Footnote] = field(default_factory=list)

    def __post_init__(self):
        self.lines = Bodyline.from_cropped(self.body)
        if self.annex:
            self.footnotes = Footnote.from_cropped(self.annex)

    @classmethod
    def extract(
        cls,
        path: Path,
        page_num: int = 2,
        terminal_y: int | None = None,
    ) -> Self | None:
        """Each `page_num` should have a `body`, and optionally an `annex`

        Args:
            path (Path): Path to the pdf file.
            page_num (int, optional): Will deduct 1 for slicing. Defaults to 2.
            terminal_y (int | None, optional): If present, refers to
                The y-axis point of the terminal page. Defaults to None.

        Returns:
            Self: Page with individual components mapped out.
        """
        if page_num <= 1:
            raise Exception("Must not be the first page.")

        page, im = get_page_and_img(path, page_num - 1)

        # preflight check to determine if blank
        if len(page.extract_text()) < 100:
            return None

        # the header line determines the start of the body proper
        header_line = get_header_line(im, page)
        if not header_line:
            raise Exception("Could not find header.")

        # necessary because of blank pages
        extracted_page_num = get_page_num(page, header_line) or 0

        # prepare common slicing borders
        cut = {"page": page, "x0": SIDE_MARGIN, "x1": page.width - SIDE_MARGIN}

        # get body_end_line and terminal_line for annex and body vertical borders
        body_end_line, terminal_line = get_annex_y_axis(im, page)
        annex = None
        if terminal_line:
            annex = PageCut(**cut, y0=body_end_line, y1=terminal_line).slice
        if terminal_y:
            body_end_line = terminal_y
        body = PageCut(**cut, y0=header_line, y1=body_end_line).slice

        return cls(body=body, annex=annex, page_num=extracted_page_num)


@dataclass
class Decision:
    """Metadata of a pdf file parsed via `get_decision()`

    Field | Description
    --:|:--
    header | The top portion of the page, usually excluded from metadata
    composition | The composition of the Supreme Court that decided the case
    category | When available, whether the case is a "Decision" or a "Resolution"
    writer | When available, the writer of the case
    notice | When True, means that there is no `category` available
    pages | A list of [Decision Pages with bodies/annexes][decision-page]
    """

    header: CroppedPage
    composition: CourtCompositionChoices
    category: DecisionCategoryChoices | None = None
    writer: str | None = None
    notice: bool = False
    pages: list[DecisionPage] = field(default_factory=list)

    @property
    def lines(self) -> Iterator[Bodyline]:
        for page in self.pages:
            yield from page.lines

    @property
    def notes(self) -> Iterator[Footnote]:
        for page in self.pages:
            yield from page.footnotes

    @classmethod
    def make_start_page(
        cls,
        page: Page,
        im: numpy.ndarray,
        start: PositionCourtComposition,
    ) -> Self | None:
        """The first page can either be a:

        1. regular `Decision` page which contains a `writer`, `category`, and `header`;
        2. a `Notice` page which will be marked by a `notice`.

        Args:
            page (Page): The pdfplumber variant of the first page
            im (numpy.ndarray): Image of the `page` that will help us get a page's
                end points `e1` and `e2`
            start (PositionCourtComposition): The previously found y-axis
                based component for slicing the `page`'s `im`

        Returns:
            Self | None: A Decision instance with the first page included.
        """
        cut = {"page": page, "x0": SIDE_MARGIN, "x1": page.width - SIDE_MARGIN}
        head = start.composition_pct_height * page.height
        e1, e2 = get_annex_y_axis(im, page)

        if ntc := PositionNotice.extract(im):
            notice_pos = ntc.position_pct_height * page.height
            body = PageCut(**cut, y0=notice_pos, y1=e1).slice
            annex = PageCut(**cut, y0=e1, y1=e2).slice if e2 else None
            return cls(
                notice=True,
                composition=start.element,
                header=PageCut(**cut, y0=head, y1=notice_pos).slice,
                pages=[DecisionPage(page_num=1, body=body, annex=annex)],
            )
        elif category := PositionDecisionCategoryWriter.extract(im):
            cat_pos = category.category_pct_height * page.height
            writer_pos = category.writer_pct_height * page.height
            body = PageCut(**cut, y0=writer_pos, y1=e1).slice
            annex = PageCut(**cut, y0=e1, y1=e2).slice if e2 else None
            return cls(
                composition=start.element,
                category=category.element,
                writer=category.writer,
                header=PageCut(**cut, y0=head, y1=cat_pos).slice,
                pages=[DecisionPage(page_num=1, body=body, annex=annex)],
            )
        return None

    def make_next_pages(self, path: Path, last_num: int, last_y: int) -> Self:
        """After the first page is created, add subsequent pages taking into
        account the terminal page and line. When the terminal page `last_num`
        is reached, stop the for-loop.

        Args:
            path (Path): Path to the pdf file.
            last_num (int): The terminal page
            last_y (int): The y-axis point of the terminal page

        Returns:
            Self: The Decision instance containing any added pages from
                the for loop.
        """
        for page in pdfplumber.open(path).pages:
            if (num := page.page_number) != 1:
                if num == last_num:
                    if page_valid := DecisionPage.extract(path, num, last_y):
                        self.pages.append(page_valid)
                        page.pdf.close()
                    break
                else:
                    if page_valid := DecisionPage.extract(path, num):
                        self.pages.append(page_valid)
        return self


def get_decision(path: Path) -> Decision:
    """From a pdf file, get metadata filled Decision with pages
    cropped into bodies and annexes until the terminal page.

    Examples:
        >>> from pathlib import Path
        >>> x = Path().cwd() / "tests" / "data" / "decision.pdf"
        >>> decision = get_decision(x)
        >>> decision.category
        <DecisionCategoryChoices.RESO: 'Resolution'>
        >>> decision.composition
        <CourtCompositionChoices.DIV2: 'Second Division'>
        >>> decision.writer
        'CARPIO, J.:'
        >>> isinstance(next(decision.lines), Bodyline)
        True
        >>> isinstance(next(decision.notes), Footnote)
        True

    Args:
        path (Path): Path to the pdf file.

    Returns:
        Self: Instance of a Decision with pages populated
    """  # noqa: E501
    page, im = get_page_and_img(path, 0)
    if not (comp := PositionCourtComposition.extract(im)):
        page.pdf.close()
        raise Exception(f"No court composition detected {path=}")
    if not (caso := Decision.make_start_page(page, im, comp)):
        page.pdf.close()
        raise Exception(f"First page unprocessed {path=}")
    if not (page_pos := get_terminal_page_pos(path)):
        page.pdf.close()
        raise Exception(f"No terminal detected {path=}")
    decision = caso.make_next_pages(path, page_pos[0], page_pos[1])
    return decision
