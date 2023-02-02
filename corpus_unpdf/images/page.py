from dataclasses import dataclass, field
from pathlib import Path
from typing import Self

import cv2
import pdfplumber
from pdfplumber.page import CroppedPage, Page

from .contours import PageCut, get_page_and_img
from .elements import (
    CourtCompositionChoices,
    DecisionCategoryChoices,
    PositionCourtComposition,
    PositionDecisionCategoryWriter,
    PositionNotice,
    get_annex_y_axis,
    get_endpageline,
    get_header_terminal,
)

TOP_MARGIN = 90
SIDE_MARGIN = 50


@dataclass
class DecisionPage:
    page_num: int
    body: CroppedPage
    annex: CroppedPage | None = None

    @classmethod
    def extract(
        cls,
        path: Path,
        page_num: int = 2,
        terminal_y: int | None = None,
    ):
        if page_num <= 1:
            raise Exception("Must not be the first page.")
        page, im = get_page_and_img(path, page_num - 1)
        cut = {"page": page, "x0": SIDE_MARGIN, "x1": page.width - SIDE_MARGIN}
        head = get_header_terminal(im, page)
        if not head:
            raise Exception("Could not find header.")

        e1, e2 = get_annex_y_axis(im, page)
        if terminal_y:
            e1 = terminal_y
        return cls(
            body=PageCut(**cut, y0=head, y1=e1).result,
            annex=PageCut(**cut, y0=e1, y1=e2).result if e2 else None,
            page_num=page_num,
        )


@dataclass
class Decision:
    header: CroppedPage
    composition: CourtCompositionChoices
    writer: str | None = None
    category: DecisionCategoryChoices | None = None
    notice: bool = False
    pages: list[DecisionPage] = field(default_factory=list)

    @classmethod
    def start_page(
        cls,
        page: Page,
        im: cv2.Mat,
        start: PositionCourtComposition,
    ) -> Self | None:
        cut = {"page": page, "x0": SIDE_MARGIN, "x1": page.width - SIDE_MARGIN}
        head = start.get_y_axis_composition(page)
        e1, e2 = get_annex_y_axis(im, page)

        if notice := PositionNotice.extract(im):
            y_pos = notice.get_y_pos(page)
            body = PageCut(**cut, y0=y_pos, y1=e1).result
            annex = PageCut(**cut, y0=e1, y1=e2).result if e2 else None
            return cls(
                notice=True,
                composition=start.element,
                header=PageCut(**cut, y0=head, y1=y_pos).result,
                pages=[DecisionPage(page_num=1, body=body, annex=annex)],
            )
        elif cat := PositionDecisionCategoryWriter.extract(im):
            cat_pos = cat.get_y_axis_category(page)
            writer_pos = cat.get_y_axis_writer(page)
            body = PageCut(**cut, y0=writer_pos, y1=e1).result
            annex = PageCut(**cut, y0=e1, y1=e2).result if e2 else None
            return cls(
                composition=start.element,
                category=cat.element,
                writer=cat.writer,
                header=PageCut(**cut, y0=head, y1=cat_pos).result,
                pages=[DecisionPage(page_num=1, body=body, annex=annex)],
            )
        return None

    def unpack_next_pages(self, target: Path) -> Self:
        if not (end := get_endpageline(target)):
            raise Exception(f"No terminal detected {target=}")
        for page in pdfplumber.open(target).pages:
            if (num := page.page_number) != 1:
                if num == end[0]:
                    nxt = DecisionPage.extract(target, num, end[1])
                    self.pages.append(nxt)
                    break
                else:
                    nxt = DecisionPage.extract(target, num)
                    self.pages.append(nxt)
        return self

    @classmethod
    def set_pages(cls, target: Path) -> Self:
        page, im = get_page_and_img(target, 0)
        if not (comp := PositionCourtComposition.extract(im)):
            raise Exception(f"No court composition detected {target=}")
        if not (caso := Decision.start_page(page, im, comp)):
            raise Exception(f"First page unprocessed {target=}")
        return caso.unpack_next_pages(target)
