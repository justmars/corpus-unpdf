from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import NamedTuple, Self

import numpy
import pdfplumber
from loguru import logger
from pdfplumber.page import CroppedPage, Page
from pdfplumber.pdf import PDF

from .src import (
    Bodyline,
    CourtCompositionChoices,
    DecisionCategoryChoices,
    Footnote,
    PageCut,
    PositionCourtComposition,
    PositionDecisionCategoryWriter,
    PositionNotice,
    get_end_page_pos,
    get_header_line,
    get_img_from_page,
    get_page_end,
    get_page_num,
    get_start_page_pos,
)


def _err(page: Page, msg: str) -> Exception:
    page.pdf.close()
    msg += f" in {page.page_number=}"
    logger.error(msg)
    raise Exception(msg)


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
    def extract_proper(
        cls,
        page: Page,
        start_y: float | int | None = None,
        end_y: float | int | None = None,
    ) -> Self:
        """
        The presence of a `header_line` and a `page_endline` determine
        what to extract from a given `page`.

        The `header_line` is the imaginary line at the top of the page.
        If the `start_y` is supplied, it means that the `header_line`
        no longer needs to be calculated.

        The `page_line` is the imaginary line at the bottom of the page
        If the `end_y` is supplied, it means that the calculated `page_line`
        ought to be replaced.

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
            raise _err(page, "No header line")

        end_of_content, e = get_page_end(im, page)
        page_line = end_y or end_of_content

        page_num = get_page_num(page, header_line) or 0
        body = PageCut.set(page=page, y0=header_line, y1=page_line)
        annex = PageCut.set(page=page, y0=end_of_content, y1=e) if e else None
        return cls(page_num=page_num, body=body, annex=(annex))


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

    composition: CourtCompositionChoices
    category: DecisionCategoryChoices | None = None
    header: CroppedPage | None = None
    writer: str | None = None
    notice: bool = False
    pages: list[DecisionPage] = field(default_factory=list)


class DecisionMeta(NamedTuple):
    start_index: int
    start_page_num: int
    start_indicator: PositionDecisionCategoryWriter | PositionNotice
    end_page_num: int
    end_page_pos: float | int

    @classmethod
    def prep(cls, path: Path):
        if not (starter := get_start_page_pos(path)):
            raise Exception("Could not detect start of content.")

        index, start_indicator = starter
        if not start_indicator:
            raise Exception("Could not detect start indicator.")

        ender = get_end_page_pos(path)
        if not ender:
            raise Exception("Could not detect end of content.")
        end_page_num, end_page_pos = ender

        return cls(
            start_index=index,
            start_page_num=index + 1,
            start_indicator=start_indicator,
            end_page_num=end_page_num,
            end_page_pos=end_page_pos,
        )

    def init(self, pdf: PDF) -> Decision:
        """Add the metadata of a Decision and extract the first page of the content
        proper which will not necessarily be page 1.

        Returns:
            Decision: A Decision instance, if all elements match.
        """
        logger.debug(f"Initialize {self=}")
        start_page = pdf.pages[self.start_index]
        if isinstance(self.start_indicator, PositionNotice):
            return Decision(
                composition=PositionCourtComposition.from_pdf(pdf).element,
                notice=True,
                pages=[
                    DecisionPage.extract_proper(
                        page=start_page,
                        start_y=self.start_indicator.position_pct_height
                        * start_page.height,
                    )
                ],
            )
        elif isinstance(self.start_indicator, PositionDecisionCategoryWriter):
            return Decision(
                composition=PositionCourtComposition.from_pdf(pdf).element,
                category=self.start_indicator.element,
                writer=self.start_indicator.writer,
                pages=[
                    DecisionPage.extract_proper(
                        page=start_page,
                        start_y=self.start_indicator.writer_pct_height
                        * start_page.height,
                    )
                ],
            )
        raise Exception("Unexpected initialization of decision.")

    def add(self, pages: list[Page]) -> Iterator[DecisionPage]:
        for nxt in pages:
            if nxt.page_number <= self.start_page_num:
                continue
            if nxt.page_number == self.end_page_num:
                logger.debug(f"Finalize {nxt.page_number=}.")
                if page_valid := DecisionPage.extract_proper(
                    page=nxt,
                    end_y=self.end_page_pos,
                ):
                    yield page_valid
                else:
                    logger.warning("Detected blank page.")
                break
            else:
                logger.debug(f"Initialize {nxt.page_number=}.")
                if page_valid := DecisionPage.extract_proper(page=nxt):
                    yield page_valid
                else:
                    logger.warning("Detected blank page.")


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
        'CARPIO. J.:'
        >>> isinstance(decision.pages[0].lines[0], Bodyline)
        True
        >>> decision.pages[0].footnotes == [] # none found, # TODO: can't seem to detect
        True

    Args:
        path (Path): Path to the pdf file.

    Returns:
        Self: Instance of a Decision with pages populated
    """  # noqa: E501
    meta = DecisionMeta.prep(path)
    with pdfplumber.open(path) as pdf:
        caso = meta.init(pdf=pdf)
        content_pages = meta.add(pages=pdf.pages)
        caso.pages.extend(content_pages)
        return caso
