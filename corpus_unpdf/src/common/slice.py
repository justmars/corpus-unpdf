from difflib import SequenceMatcher
from typing import NamedTuple

import cv2
import numpy
import pytesseract
from pdfplumber._typing import T_bbox
from pdfplumber.page import CroppedPage, Page


def get_contours(img: numpy.ndarray, rectangle_size: tuple[int, int]) -> list:
    """Generally follows the strategy outlined here:

    1. [Youtube video](https://www.youtube.com/watch?v=ZeCRe9sNFwk&list=PL2VXyKi-KpYuTAZz__9KVl1jQz74bDG7i&index=11)
    2. [Stack Overflow answer](https://stackoverflow.com/a/57262099)

    The structuring element used will be a rectangle of dimensions
    specified in `rectangle_size`. After dilating the image,
    the contours can be enumerated for further processing and
    matching, e.g. after the image is transformed, can find
    which lines appear in the center or in the top right quadrant, etc.

    Args:
        img (numpy.ndarray): The opencv formatted image
        rectangle_size (tuple[int, int]): The width and height to morph the characters

    Returns:
        list: The contours found based on the specified structuring element
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
    im: numpy.ndarray, text_to_match: str
) -> tuple[int, int, int, int] | None:
    """With a image `im`, get all contours found in the center
    of the image and then for each of these matches, if they
    are text resembling `text_to_match`, extract the coordinates of
    such contours.

    Examples:
        >>> from corpus_unpdf.src.common.fetch import get_page_and_img
        >>> from pathlib import Path
        >>> x = Path().cwd() / "tests" / "data" / "decision.pdf"
        >>> page, im = get_page_and_img(x, 0)
        >>> get_centered_coordinates(im, 'Decision') # None found
        >>> get_centered_coordinates(im, 'Resolution')
        (1043, 2118, 614, 72)

    Args:
        im (numpy.ndarray): The base image to look for text
        text_to_match (str): The words that should match

    Returns:
        tuple[int, int, int, int] | None: (x, y, w, h) pixels representing
            `cv2.boundingRect`, if found.
    """
    _, im_w, _ = im.shape
    cnts = get_contours(im, (100, 30))
    for cnt in cnts:
        x, y, w, h = cv2.boundingRect(cnt)
        if is_centered(im_w, x, w):
            sliced_im = im[y : y + h, x : x + w]
            if sliced_txt := pytesseract.image_to_string(sliced_im):
                txt_a = text_to_match.upper()
                txt_b = sliced_txt.upper()
                if SequenceMatcher(None, a=txt_a, b=txt_b).ratio() > 0.7:
                    return x, y, w, h
    return None


class PageCut(NamedTuple):
    """Fields:

    field | type | description
    --:|:--|:--
    page | pdfplumber.page.Page | The page to cut
    x0 | float or int | The x axis where the slice will start
    x1 | float or int | The x axis where the slice will terminate
    y0 | float or int | The y axis where the slice will start
    y1 | float or int | The y axis where the slice will terminate

    When the above fields are populated, the `@slice` property describes
    the area of the page that will be used to extract text from.

    Examples:
        >>> from pathlib import Path
        >>> from corpus_unpdf.src.common.fetch import get_page_and_img
        >>> x = Path().cwd() / "tests" / "data" / "decision.pdf"
        >>> page, im = get_page_and_img(x, 0)
        >>> page.height
        948.72
        >>> cutpage = PageCut(page=page, x0=100, x1=200, y0=100, y1=200).slice
        >>> cutpage.height
        100
    """

    page: Page
    x0: float | int
    x1: float | int
    y0: float | int
    y1: float | int

    @property
    def slice(self) -> CroppedPage:
        """Unlike slicing from an image based on a `numpy.ndarray`, a page cut
        implies a page derived from `pdfplumber`. The former is based on pixels;
        the latter on points.

        Returns:
            CroppedPage: The page crop where to extract text from.
        """
        box: T_bbox = (self.x0, self.y0, self.x1, self.y1)
        return self.page.crop(box, relative=False, strict=True)
