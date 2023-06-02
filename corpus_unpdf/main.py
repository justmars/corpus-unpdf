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
class OpinionCollection(Collection):
    """Inherits from `start_ocr`'s Collection.

    Using `OpinionCollection.set(<path-to-pdf)` can extract content and metadata of the file.
    """  # noqa: E501

    ...

    @classmethod
    def set(cls, path: Path):
        """Limited extraction: only interested in content unlike decisions where metadata is relevant. Also assumes first page will always be the logical start."""  # noqa: E501
        first_page = Collection.preliminary_page(path)
        return Collection.make(path, preliminary_page=first_page)


@dataclass
class DecisionCollection(Collection, FrontpageMeta):
    """Inherits from `start_ocr`'s `Collection` with custom `FrontpageMeta`.

    Using `DecisionCollection.set(<path-to-pdf)` can extract content and metadata of the file.
    """  # noqa: E501

    ...

    @classmethod
    def set(cls, path: Path) -> Self:
        """From a _*.pdf_ file found in `path`, extract relevant metadata to generate a decision having content pages. Each of which will contain a body and, likely, an annex for footnotes.

        Examples:
            >>> x = Path().cwd() / "tests" / "data" / "decision.pdf"
            >>> decision = DecisionCollection.set(x)
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
            caso = cls.init(pdf=pdf, pos=pos)  # all pages
            caso.limit_pages(pages=pdf.pages, pos=pos)  # limited pages
            caso.join_segments()
            caso.join_annexes()
            return caso

    @classmethod
    def init(cls, pdf: PDF, pos: PositionMeta) -> Self:
        """Extract first page of the content proper which may not necessarily be page 1.

        Args:
            pdf (PDF): The `pdfplumber`-formatted PDF
            pos (PositionMeta): Contains true start and end position / pages

        Returns:
            Self: DecisionCollection instance.
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

    def limit_pages(self, pages: list[Page], pos: PositionMeta):
        """Ensure only  pages covered by the `pos` are included in the final Decision collection."""  # noqa: E501
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
