from corpus_unpdf.images.contours import get_centered_coordinates
from typing import NamedTuple
from enum import Enum
from typing import Self
import cv2


class NoticeChoices(Enum):
    NOTICE = "Notice"


class PositionNotice(NamedTuple):
    element: NoticeChoices
    coordinates: tuple[int, int, int, int]

    @classmethod
    def extract(cls, im: cv2.Mat) -> Self | None:
        for member in NoticeChoices:
            if c := get_centered_coordinates(im, member.value):
                return cls(element=member, coordinates=c)
        return None
