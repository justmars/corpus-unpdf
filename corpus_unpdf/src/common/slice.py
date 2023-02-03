from difflib import SequenceMatcher

from typing import NamedTuple

import cv2
import pytesseract
from pdfplumber.page import CroppedPage, Page
from .contour import get_contours
from pdfplumber._typing import T_bbox


def is_centered(im_w, x, w) -> bool:
    x0_mid_left = (1 * im_w) / 3 < x < im_w / 2
    x1_mid_right = (2 * im_w) / 3 > x + w > im_w / 2
    criteria = [x0_mid_left, x1_mid_right, w > 200]
    return all(criteria)


def get_centered_coordinates(
    im: cv2.Mat, text_to_match: str
) -> tuple[int, int, int, int] | None:
    _, im_w, _ = im.shape
    cnts = get_contours(im, (100, 30))
    for text_like_contour in cnts:
        x, y, w, h = cv2.boundingRect(text_like_contour)
        if is_centered(im_w, x, w):
            sliced_im = im[y : y + h, x : x + w]
            if sliced_txt := pytesseract.image_to_string(sliced_im):
                txt_a = text_to_match.upper()
                txt_b = sliced_txt.upper()
                if SequenceMatcher(None, a=txt_a, b=txt_b).ratio() > 0.7:
                    return x, y, w, h
    return None


class PageCut(NamedTuple):
    """Slice `page` vertically based on criteria:

    page (Page): the pdfplumber.page.Page based on `im`
    x0 (float | int): The x axis where the slice will start
    x1 (float | int): The x axis where the slice will terminate
    y0 (float | int): The y axis where the slice will start
    y1 (float | int): The y axis where the slice will terminate
    """

    page: Page
    x0: float | int
    x1: float | int
    y0: float | int
    y1: float | int

    @property
    def result(self) -> CroppedPage:
        box: T_bbox = (self.x0, self.y0, self.x1, self.y1)
        return self.page.crop(box, relative=False, strict=True)
