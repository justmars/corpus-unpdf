from .elements import (
    PositionCourtComposition,
    CourtCompositionChoices,
    PositionDecisionCategoryWriter,
    DecisionCategoryChoices,
    PositionNotice,
    get_footnote_coordinates,
)
import cv2
from .contours import get_page_and_img
from dataclasses import dataclass

from pathlib import Path
from pdfplumber.page import CroppedPage, Page

X0 = 75
"""Note 96 pixels = 1 inch, used to get left margin"""

X1 = 75
"""Note 96 pixels = 1 inch, used to get right margin"""

PERCENT_OF_MAX_PAGE = 0.92


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
    def get_fn_xy(cls, im: cv2.Mat, page: Page) -> tuple[float, float | None]:
        im_h, _, _ = im.shape
        fn = get_footnote_coordinates(im)
        if fn:
            _, y, _, _ = fn
            fn_line_end = y / im_h
            e = fn_line_end * page.height
            return e, PERCENT_OF_MAX_PAGE * page.height
        return PERCENT_OF_MAX_PAGE * page.height, None

    @classmethod
    def _crop(cls, page: Page, box) -> CroppedPage:
        return page.crop(box, relative=False, strict=True)

    @classmethod
    def extract(cls, path: Path):
        annex = None
        page, im = get_page_and_img(path, 0)
        w = page.width - X1

        comp = PositionCourtComposition.extract(im)
        if not comp:
            raise Exception(f"No court composition detected {path=}")
        head_start = comp.get_y_axis_composition(page)

        fn_start, fn_end = cls.get_fn_xy(im, page)
        if fn_start and fn_end:
            annex = cls._crop(page, (X0, fn_start, w, fn_end))

        if is_notice := PositionNotice.extract(im):
            head_end = is_notice.get_y_axis_position(page)
            return cls(
                header=cls._crop(page, (X0, head_start, w, head_end)),
                body=cls._crop(page, (X0, head_end, w, fn_start)),
                annex=annex,
                composition=comp.element,
                notice=True,
            )
        elif cat := PositionDecisionCategoryWriter.extract(im):
            head_end = cat.get_y_axis_category(page)
            body_start = cat.get_y_axis_writer(page)
            return cls(
                header=cls._crop(page, (X0, head_start, w, head_end)),
                body=cls._crop(page, (X0, body_start, w, fn_start)),
                annex=annex,
                composition=comp.element,
                category=cat.element,
                writer=cat.writer,
            )
