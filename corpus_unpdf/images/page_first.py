from dataclasses import dataclass
from pathlib import Path

import cv2
from pdfplumber.page import CroppedPage, Page

from .contours import get_page_and_img
from .elements import (
    CourtCompositionChoices,
    DecisionCategoryChoices,
    PositionCourtComposition,
    PositionDecisionCategoryWriter,
    PositionNotice,
    get_footnote_coordinates,
)

X = 75
"""Note 96 pixels = 1 inch, used to get left margin"""

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
    def get_annex_y_axis(
        cls, im: cv2.Mat, page: Page
    ) -> tuple[float, float | None]:
        """Given an `im`, detect the footnote line of the annex and return
        relevant points in the y-axis as a tuple.

        Args:
            im (cv2.Mat): the openCV image that may contain a footnote line
            page (Page): the pdfplumber.page.Page based on `im`

        Returns:
            tuple[float, float | None]: If footnote line exists:

                1. Value 1 = y-axis of the page;
                2. Value 2: maximum point in y-axis

                If footnote line does not exist:

                1. Value 1 = maximum point in y-axis
                2. Value 2: None
        """
        im_h, _, _ = im.shape
        fn = get_footnote_coordinates(im)
        y1 = PERCENT_OF_MAX_PAGE * page.height
        if fn:
            _, y, _, _ = fn
            fn_line_end = y / im_h
            y0 = fn_line_end * page.height
            return y0, y1
        return y1, None

    @classmethod
    def _slice(cls, page: Page, y0: float, y1: float) -> CroppedPage:
        """Slice `page` vertically based on criteria `y` and `h`.

        Args:
            page (Page): the pdfplumber.page.Page based on `im`
            y0 (float): The y axis where the slice will start
            y1 (float): The y axis where the slice will terminate

        Returns:
            CroppedPage: _description_
        """
        return page.crop(
            (X, y0, page.width - X, y1),
            relative=False,
            strict=True,
        )

    @classmethod
    def extract(cls, path: Path):
        annex = None
        p, im = get_page_and_img(path, 0)
        comp = PositionCourtComposition.extract(im)
        if not comp:
            raise Exception(f"No court composition detected {path=}")

        hd_start = comp.get_y_axis_composition(p)
        fn_start, fn_end = cls.get_annex_y_axis(im, p)
        if fn_start and fn_end:
            annex = cls._slice(p, fn_start, fn_end)
        preset = {"annex": annex, "composition": comp.element}

        if notice := PositionNotice.extract(im):
            return cls(
                header=cls._slice(p, hd_start, notice.get_y_pos(p)),
                body=cls._slice(p, notice.get_y_pos(p), fn_start),
                notice=True,
                **preset,
            )
        elif cat := PositionDecisionCategoryWriter.extract(im):
            return cls(
                header=cls._slice(p, hd_start, cat.get_y_axis_category(p)),
                body=cls._slice(p, cat.get_y_axis_writer(p), fn_start),
                category=cat.element,
                writer=cat.writer,
                **preset,
            )
