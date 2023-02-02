from corpus_unpdf.images.contours import get_centered_coordinates
from typing import NamedTuple
from enum import Enum
from typing import Self
import cv2
import pytesseract


class DecisionCategory(Enum):
    CASO = "Decision"
    RESO = "Resolution"


class PositionDecisionCategoryWriter(NamedTuple):
    element: DecisionCategory
    coordinates: tuple[int, int, int, int]
    writer: str

    @classmethod
    def extract(cls, im: cv2.Mat) -> Self | None:
        for member in DecisionCategory:
            if xywh := get_centered_coordinates(im, member.value):
                y = xywh[1]
                y0, y1 = y + 100, y + 250
                writer_box = im[y0:y1]
                writer = pytesseract.image_to_string(writer_box).strip()
                return cls(element=member, coordinates=xywh, writer=writer)
        return None
