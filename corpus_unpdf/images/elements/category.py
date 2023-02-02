from enum import Enum
from typing import NamedTuple, Self

import cv2
import pytesseract
from pdfplumber.page import Page

from corpus_unpdf.images.contours import get_centered_coordinates


class DecisionCategoryChoices(Enum):
    CASO = "Decision"
    RESO = "Resolution"


class PositionDecisionCategoryWriter(NamedTuple):
    """
    A note on `_pct_height`:

    With pixel of height `y` (y-axis) as numerator of an image with total
    max height `im_h`, get the fractional height.
    """

    element: DecisionCategoryChoices
    coordinates: tuple[int, int, int, int]
    writer: str
    category_pct_height: float
    writer_pct_height: float

    @classmethod
    def extract(cls, im: cv2.Mat) -> Self | None:
        im_h, _, _ = im.shape
        for member in DecisionCategoryChoices:
            if xywh := get_centered_coordinates(im, member.value):
                y = xywh[1]
                y0, y1 = y + 100, y + 225
                writer_box = im[y0:y1]
                return cls(
                    element=member,
                    coordinates=xywh,
                    writer=pytesseract.image_to_string(writer_box).strip(),
                    category_pct_height=y / im_h,
                    writer_pct_height=y1 / im_h,
                )
        return None

    def get_y_axis_category(self, page: Page):
        return self.category_pct_height * page.height

    def get_y_axis_writer(self, page: Page):
        return self.writer_pct_height * page.height
