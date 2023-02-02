from dataclasses import dataclass
from pathlib import Path

from pdfplumber.page import CroppedPage

from .contours import PageCut, get_page_and_img
from .elements import (
    CourtCompositionChoices,
    DecisionCategoryChoices,
    PositionCourtComposition,
    PositionDecisionCategoryWriter,
    PositionNotice,
    get_annex_y_axis,
)

TOP_MARGIN = 90
SIDE_MARGIN = 75


@dataclass
class FirstPage:
    header: CroppedPage
    body: CroppedPage
    composition: CourtCompositionChoices
    notice: bool = False
    writer: str | None = None
    category: DecisionCategoryChoices | None = None
    annex: CroppedPage | None = None

    @classmethod
    def extract(cls, path: Path):
        page, im = get_page_and_img(path, 0)
        comp = PositionCourtComposition.extract(im)
        if not comp:
            raise Exception(f"No court composition detected {path=}")

        cut = {"page": page, "x0": SIDE_MARGIN, "x1": page.width - SIDE_MARGIN}
        head = comp.get_y_axis_composition(page)
        e1, e2 = get_annex_y_axis(im, page)

        if notice := PositionNotice.extract(im):
            y_pos = notice.get_y_pos(page)
            return cls(
                header=PageCut(**cut, y0=head, y1=y_pos).result,
                body=PageCut(**cut, y0=y_pos, y1=e1).result,
                annex=PageCut(**cut, y0=e1, y1=e2).result if e2 else None,
                notice=True,
                composition=comp.element,
            )
        elif cat := PositionDecisionCategoryWriter.extract(im):
            cat_pos = cat.get_y_axis_category(page)
            writer_pos = cat.get_y_axis_writer(page)
            return cls(
                header=PageCut(**cut, y0=head, y1=cat_pos).result,
                body=PageCut(**cut, y0=writer_pos, y1=e1).result,
                annex=PageCut(**cut, y0=e1, y1=e2).result if e2 else None,
                composition=comp.element,
                category=cat.element,
                writer=cat.writer,
            )


@dataclass
class NextPage:
    page_num: int
    body: CroppedPage
    annex: CroppedPage | None = None

    @classmethod
    def extract_page(cls, path: Path, page_num: int = 1):
        if page_num <= 0:
            raise Exception("Must not be the first page.")
        page, im = get_page_and_img(path, page_num)
        cut = {"page": page, "x0": SIDE_MARGIN, "x1": page.width - SIDE_MARGIN}
        e1, e2 = get_annex_y_axis(im, page)
        return cls(
            body=PageCut(**cut, y0=TOP_MARGIN, y1=e1).result,
            annex=PageCut(**cut, y0=e1, y1=e2).result if e2 else None,
            page_num=page_num,
        )
