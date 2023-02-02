from difflib import SequenceMatcher
from pathlib import Path
from typing import NamedTuple

import cv2
import numpy
import pdfplumber
import pytesseract
from pdfplumber.page import CroppedPage, Page
from PIL import Image


def get_page_and_img(
    pdfpath: str | Path, pagenum: int
) -> tuple[Page, cv2.Mat]:
    pdf = pdfplumber.open(pdfpath)
    page = pdf.pages[pagenum]
    img = page.to_image(resolution=300)
    if isinstance(img.original, Image.Image):
        cv2_image = cv2.cvtColor(numpy.array(img.original), cv2.COLOR_RGB2BGR)
        return page, cv2_image
    raise Exception("Could not get CV2-formatted image.")


def get_contours(img: cv2.Mat, rectangle_size: tuple[int, int]):
    """Generally follows the strategy outlined here:

    1. [Youtube video](https://www.youtube.com/watch?v=ZeCRe9sNFwk&list=PL2VXyKi-KpYuTAZz__9KVl1jQz74bDG7i&index=11)
    2. [Stack Overflow answer](https://stackoverflow.com/a/57262099)

    The structuring element used will be a rectangle of dimensions
    specified in `rectangle_size`. After dilating the image,
    the contours can be enumerated for further processing and
    matching, e.g. after the image is transformed, can find
    which lines appear in the center or in the top right quadrant, etc.

    Args:
        img (cv2.Mat): The opencv formatted image
        rectangle_size (tuple[int, int]): The width and height to morph the characters

    Returns:
        _type_: The contours found based on the specified structuring element
    """  # noqa: E501
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (7, 7), 0)
    thresh = cv2.threshold(
        blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )[1]
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, rectangle_size)
    dilate = cv2.dilate(thresh, kernel, iterations=1)
    cv2.imwrite("temp/sample_dilated.png", dilate)
    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    return sorted(cnts, key=lambda x: cv2.boundingRect(x)[1])


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
    x0 (float): The x axis where the slice will start
    x1 (float): The x axis where the slice will terminate
    y0 (float): The y axis where the slice will start
    y1 (float): The y axis where the slice will terminate
    """

    page: Page
    x0: float
    x1: float
    y0: float
    y1: float

    @property
    def result(self) -> CroppedPage:
        return self.page.crop(
            (self.x0, self.y0, self.x1, self.y1),
            relative=False,
            strict=True,
        )
