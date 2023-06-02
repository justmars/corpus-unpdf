import logging
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import NamedTuple

import pdfplumber
from pdfplumber.page import CroppedPage, Page
from pdfplumber.pdf import PDF
from start_ocr import Bodyline, Content, Footnote
from start_ocr.content import Collection

from ._markers import (
    CourtCompositionChoices,
    DecisionCategoryChoices,
    PositionCourtComposition,
    PositionDecisionCategoryWriter,
    PositionNotice,
)
from ._positions import get_end_page_pos, get_start_page_pos

logger = logging.getLogger(__name__)


@dataclass
class OpinionCollection(Collection):
    ...

    @classmethod
    def set(cls, path: Path):
        first_page = Collection.preliminary_page(path)
        return Collection.make(path, preliminary_page=first_page)


@dataclass
class DecisionCollectionVariant:
    """Metadata of a pdf file parsed via `get_decision()`

    Field | Description
    --:|:--
    `composition` | The composition of the Supreme Court that decided the case
    `category` | When available, whether the case is a "Decision" or a "Resolution"
    `header` | The top portion of the page, usually excluded from metadata
    `writer` | When available, the writer of the case
    `notice` | When True, means that there is no `category` available
    `pages` | A list of `Content` pages, see `start-ocr`
    `body` | The compiled string consisting of each page's `body_text`
    `annex` | The compiled string consisting of each page's `annex_text`, if existing
    `segments` | Each `Bodyline` of the body's text, see `start-ocr`
    `footnotes` | Each `Footnote` of the body's annex, see `start-ocr`
    """

    composition: CourtCompositionChoices
    category: DecisionCategoryChoices | None = None
    header: CroppedPage | None = None
    writer: str | None = None
    notice: bool = False
    pages: list[Content] = field(default_factory=list)
    segments: list[Bodyline] = field(default_factory=list)
    footnotes: list[Footnote] = field(default_factory=list)
    body: str = ""
    annex: str = ""

    def __repr__(self) -> str:
        return f"Decision {self.composition.value}, pages {len(self.pages)}"

    def construct(self):
        for page in self.pages:
            self.body += f"\n\n{page.body_text}"
            self.segments.extend(page.segments)
            if page.annex_text:
                self.annex += f"\n\n{page.annex_text}"
                self.footnotes.extend(page.footnotes)
        return self


class DecisionMeta(NamedTuple):
    """Metadata required to create a DecisionCollectionVariant.

    Field | Type | Description
    --:|:--:|:--
    `start_index` | int | The zero-based integer `x`, i.e. get specific `pdfplumber.pages[x]`
    `start_page_num` | int | The 1-based integer to describe human-readable page number
    `start_indicator` | [PositionDecisionCategoryWriter][decision-category-writer] or [PositionNotice][notice] | Marking the start of the content proper
    `writer` | str | When [PositionDecisionCategoryWriter][decision-category-writer]  is selected, the writer found underneath the category
    `notice` | bool | Will be marked `True`, if [PositionNotice][notice] is selected; default is `False`.
    `pages` | list[Content] | A list of pages having material content
    """  # noqa: E501

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

    def init(self, pdf: PDF) -> DecisionCollectionVariant:
        """Add the metadata of a DecisionCollectionVariant and extract the first page of the content proper which may not necessarily be page 1.

        Returns:
            DecisionCollectionVariant: A Decision instance, if all elements match.
        """  # noqa: E501
        logger.debug(f"Initialize {self=}")
        composition = PositionCourtComposition.from_pdf(pdf).element
        start_page = pdf.pages[self.start_index]
        if isinstance(self.start_indicator, PositionNotice):
            return DecisionCollectionVariant(
                composition=composition,
                notice=True,
                pages=[
                    Content.set(
                        page=start_page,
                        start_y=self.start_indicator.position_pct_height
                        * start_page.height,
                    )
                ],
            )
        elif isinstance(self.start_indicator, PositionDecisionCategoryWriter):
            return DecisionCollectionVariant(
                composition=composition,
                category=self.start_indicator.element,
                writer=self.start_indicator.writer,
                pages=[
                    Content.set(
                        page=start_page,
                        start_y=self.start_indicator.writer_pct_height
                        * start_page.height,
                    )
                ],
            )
        raise Exception("Unexpected initialization of decision.")

    def add(self, pages: list[Page]) -> Iterator[Content]:
        for nxt in pages:
            if nxt.page_number <= self.start_page_num:
                continue
            if nxt.page_number == self.end_page_num:
                logger.debug(f"Finalize {nxt.page_number=}.")
                if page_valid := Content.set(page=nxt, end_y=self.end_page_pos):
                    yield page_valid
                else:
                    logger.warning("Detected blank page.")
                break
            else:
                logger.debug(f"Initialize {nxt.page_number=}.")
                if page_valid := Content.set(page=nxt):
                    yield page_valid
                else:
                    logger.warning("Detected blank page.")


def get_decision(path: Path) -> DecisionCollectionVariant:
    """From a _*.pdf_ file found in `path`, extract relevant metadata to generate a decision having content pages. Each of which will contain a body and, likely, an annex for footnotes.

    Examples:
        >>> x = Path().cwd() / "tests" / "data" / "decision.pdf"
        >>> decision = get_decision(x)
        >>> decision.category
        <DecisionCategoryChoices.RESO: 'Resolution'>
        >>> decision.composition
        <CourtCompositionChoices.DIV2: 'Second Division'>
        >>> decision.writer
        'CARPIO. J.:'
        >>> len(decision.pages) # total page count
        5
        >>> isinstance(decision.pages[0], Content) # first page
        True
        >>> isinstance(decision.segments[0], Bodyline)
        True
        >>> isinstance(decision.footnotes[0], Footnote)
        True
        >>> len(decision.footnotes) # TODO: limited number detected; should be 15
        10

    Args:
        path (Path): Path to the pdf file.

    Returns:
        Self: Instance of a Decision with pages populated
    """  # noqa: E501
    meta = DecisionMeta.prep(path)
    with pdfplumber.open(path) as pdf:
        caso = meta.init(pdf=pdf)  # create all the pages of the decision
        caso.pages.extend(meta.add(pages=pdf.pages))
        caso.construct()  # construct full decision
        return caso
