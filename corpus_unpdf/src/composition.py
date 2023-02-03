from enum import Enum
from typing import NamedTuple, Self

import cv2
from pdfplumber.page import Page

from .common import get_centered_coordinates


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
