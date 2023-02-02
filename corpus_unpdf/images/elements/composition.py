from corpus_unpdf.images.contours import get_centered_coordinates
from typing import NamedTuple
from enum import Enum
from typing import Self
import cv2
from pdfplumber.page import Page


class CourtCompositionChoices(Enum):
    ENBANC = "En Banc"
    DIV1 = "First Division"
    DIV2 = "Second Division"
    DIV3 = "Third Division"


class PositionCourtComposition(NamedTuple):
    """
    A note on `_pct_height`:

    With pixel of height `y` (y-axis) as numerator of an image with total
    max height `im_h`, get the fractional height.
    """

    element: CourtCompositionChoices
    coordinates: tuple[int, int, int, int]
    composition_pct_height: float

    @classmethod
    def extract(cls, im: cv2.Mat) -> Self | None:
        im_h, _, _ = im.shape
        for member in CourtCompositionChoices:
            if xywh := get_centered_coordinates(im, member.value):
                y, h = xywh[1], xywh[3]
                return cls(
                    element=member,
                    coordinates=xywh,
                    composition_pct_height=(y + h) / im_h,
                )
        return None

    def get_y_axis_composition(self, page: Page):
        return self.composition_pct_height * page.height
