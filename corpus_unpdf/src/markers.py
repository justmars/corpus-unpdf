from enum import Enum
from typing import NamedTuple, Self
import pytesseract
import cv2

from .common import get_centered_coordinates

PERCENT_OF_MAX_PAGE = 0.92
TOP_MARGIN = 90
SIDE_MARGIN = 50


class NoticeChoices(Enum):
    NOTICE = "Notice"


class CourtCompositionChoices(Enum):
    ENBANC = "En Banc"
    DIV1 = "First Division"
    DIV2 = "Second Division"
    DIV3 = "Third Division"


class DecisionCategoryChoices(Enum):
    CASO = "Decision"
    RESO = "Resolution"


class PositionNotice(NamedTuple):
    element: NoticeChoices
    coordinates: tuple[int, int, int, int]
    position_pct_height: float

    @classmethod
    def extract(cls, im: cv2.Mat) -> Self | None:
        im_h, _, _ = im.shape
        for member in NoticeChoices:
            if xywh := get_centered_coordinates(im, member.value):
                y, h = xywh[1], xywh[3]
                return cls(
                    element=member,
                    coordinates=xywh,
                    position_pct_height=(y + h) / im_h,
                )
        return None


class PositionCourtComposition(NamedTuple):
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


class PositionDecisionCategoryWriter(NamedTuple):
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
