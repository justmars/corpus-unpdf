from enum import Enum
from typing import NamedTuple, Self

import cv2
from pdfplumber.page import Page

from corpus_unpdf.images.contours import get_centered_coordinates


class NoticeChoices(Enum):
    NOTICE = "Notice"


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

    def get_y_pos(self, page: Page):
        return self.position_pct_height * page.height
