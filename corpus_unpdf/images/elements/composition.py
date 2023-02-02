from corpus_unpdf.images.contours import get_centered_coordinates
from typing import NamedTuple
from enum import Enum
from typing import Self
import cv2


class CourtCompositionChoices(Enum):
    ENBANC = "En Banc"
    DIV1 = "First Division"
    DIV2 = "Second Division"
    DIV3 = "Third Division"


class PositionCourtComposition(NamedTuple):
    element: CourtCompositionChoices
    coordinates: tuple[int, int, int, int]

    @classmethod
    def extract(cls, im: cv2.Mat) -> Self | None:
        for member in CourtCompositionChoices:
            if c := get_centered_coordinates(im, member.value):
                return cls(element=member, coordinates=c)
        return None
