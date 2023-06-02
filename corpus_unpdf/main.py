import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Self

import pdfplumber
from pdfplumber.page import Page
from pdfplumber.pdf import PDF
from start_ocr import Content
from start_ocr.content import Collection

from ._markers import (
    FrontpageMeta,
    PositionCourtComposition,
    PositionDecisionCategoryWriter,
    PositionNotice,
)
from ._positions import PositionMeta

logger = logging.getLogger(__name__)


@dataclass
class SeparateOpinionPages(Collection):
    """Handles content and metadata of separate opinions, i.e. the concurring, dissenting opinions to a [main
    opinion][mainopinionpages] of a _Decision_ or _Resolution_.

    Given a PDF file, can use `SeparateOpinionPages.set(<path-to-pdf)` to extract _content pages (only)_ of the file. The fields of this data structure inherits from `start_ocr`'s `Collection`.
    """  # noqa: E501

    ...

    @classmethod
    def set(cls, path: Path):
        """Limited extraction: only interested in content unlike decisions where metadata is relevant. Also assumes first page will always be the logical start.

        Examples:
            >>> x = Path().cwd() / "tests" / "data" / "opinion.pdf"
            >>> opinion = SeparateOpinionPages.set(x)
            >>> len(opinion.pages) # total page count
            10
            >>> from start_ocr import Bodyline, Footnote, Content
            >>> isinstance(opinion.pages[0], Content) # first page
            True
            >>> isinstance(opinion.segments[0], Bodyline)
            True
            >>> isinstance(opinion.footnotes[0], Footnote)
            True
        """  # noqa: E501
        first_page = Collection.preliminary_page(path)  # uses the sample execution
        return Collection.make(path, preliminary_page=first_page)


@dataclass
class MainOpinionPages(Collection, FrontpageMeta):
    """The main opinion of a _Decision_ or _Resolution_, specifically its front and last pages, is formatted differenly from [separate opinions][separateopinionpages]. The following metadata are required to be parsed:

    1. [Composition][court-composition], i.e. whether _En Banc_ or by divison.
    2. [Category][decision-category-writer], i.e. whether a _Decision_ or a _Resolution_.
    2. [Writer][decision-category-writer], i.e. who penned the main opinion.
    3. [Notice][notice], i.e. whether it is of a particular category of decisions.

    Given a PDF file, can use `MainOpinionPages.set(<path-to-pdf)` to extract content pages _and the above metadata_ of the file. The fields of this data structure inherits from `start_ocr`'s `Collection` with a custom `FrontpageMeta`.
    """  # noqa: E501

    ...

    @classmethod
    def set(cls, path: Path) -> Self:
        """From a _*.pdf_ file found in `path`, extract relevant metadata to generate a decision having content pages. Each of which will contain a body and, likely, an annex for footnotes.

        Examples:
            >>> x = Path().cwd() / "tests" / "data" / "decision.pdf"
            >>> decision = MainOpinionPages.set(x)
            >>> decision.category
            <DecisionCategoryChoices.RESO: 'Resolution'>
            >>> decision.composition
            <CourtCompositionChoices.DIV2: 'Second Division'>
            >>> decision.writer
            'CARPIO. J.:'
            >>> len(decision.pages) # total page count
            5
            >>> from start_ocr import Bodyline, Footnote, Content
            >>> isinstance(decision.pages[0], Content) # first page
            True
            >>> isinstance(decision.segments[0], Bodyline)
            True
            >>> isinstance(decision.footnotes[0], Footnote)
            True
            >>> len(decision.footnotes) # TODO: limited number detected; should be 15
            10
        """  # noqa: E501
        pos = PositionMeta.prep(path)
        with pdfplumber.open(path) as pdf:
            caso = cls._init(pdf=pdf, pos=pos)  # all pages
            caso._limit_pages(pages=pdf.pages, pos=pos)  # limited pages
            caso.join_segments()
            caso.join_annexes()
            return caso

    @classmethod
    def _init(cls, pdf: PDF, pos: PositionMeta) -> Self:
        """Extract first page of the content proper which may not necessarily be page 1.

        Args:
            pdf (PDF): The `pdfplumber`-formatted PDF
            pos (PositionMeta): Contains true start and end position / pages

        Returns:
            Self: MainOpinionPages instance.
        """
        start_page = pdf.pages[pos.start_index]
        if isinstance(pos.start_indicator, PositionNotice):
            return cls(
                composition=PositionCourtComposition.from_pdf(pdf).element,
                notice=True,
                pages=[
                    Content.set(
                        page=start_page,
                        start_y=pos.start_indicator.position_pct_height
                        * start_page.height,
                    )
                ],
            )
        elif isinstance(pos.start_indicator, PositionDecisionCategoryWriter):
            return cls(
                composition=PositionCourtComposition.from_pdf(pdf).element,
                category=pos.start_indicator.element,
                writer=pos.start_indicator.writer,
                pages=[
                    Content.set(
                        page=start_page,
                        start_y=pos.start_indicator.writer_pct_height
                        * start_page.height,
                    )
                ],
            )
        raise Exception("Unexpected initialization of decision.")

    def _limit_pages(self, pages: list[Page], pos: PositionMeta):
        """Only add pages included in the `pos` metadata when generating the Decision collection."""  # noqa: E501
        for nxt in pages:
            if nxt.page_number <= pos.start_page_num:
                continue

            if nxt.page_number == pos.end_page_num:
                logger.debug(f"Finalize {nxt.page_number=}.")
                if page_valid := Content.set(page=nxt, end_y=pos.end_page_pos):
                    self.pages.append(page_valid)
                else:
                    logger.warning("Detected blank page.")
                break
            else:
                logger.debug(f"Initialize {nxt.page_number=}.")
                if page_valid := Content.set(page=nxt):
                    self.pages.append(page_valid)
                else:
                    logger.warning("Detected blank page.")
