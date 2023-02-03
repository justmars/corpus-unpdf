import cv2
import numpy
from pdfplumber.page import Page

from .common import get_contours
from .markers import PERCENT_OF_MAX_PAGE


def get_footnote_coordinates(
    img: numpy.ndarray,
) -> tuple[int, int, int, int] | None:
    """The footnote line; since we know full image's shape, we can extract max height,
    then use this as the denominator (e.g. 3900) and the matching line described
    in boundingRect as the numerator.

    Args:
        img (numpy.ndarray): The open CV image

    Returns:
        float | None: percentage (e.g. ~0.893) of the y-axis
    """

    im_h, _, _ = img.shape
    for c in get_contours(img, (50, 10)):
        x, y, w, h = cv2.boundingRect(c)
        if w > 400 and y > im_h / 2 and h < 40:
            return x, y, w, h
    return None


def get_annex_y_axis(
    im: numpy.ndarray, page: Page
) -> tuple[float, float | None]:
    """Given an `im`, detect the footnote line of the annex and return
    relevant points in the y-axis as a tuple.

    Args:
        im (numpy.ndarray): the openCV image that may contain a footnote line
        page (Page): the pdfplumber.page.Page based on `im`

    Returns:
        tuple[float, float | None]: If footnote line exists:

            1. Value 1 = y-axis of the page;
            2. Value 2: maximum point in y-axis

            If footnote line does not exist:

            1. Value 1 = maximum point in y-axis
            2. Value 2: None
    """
    im_h, _, _ = im.shape
    fn = get_footnote_coordinates(im)
    y1 = PERCENT_OF_MAX_PAGE * page.height
    if fn:
        _, y, _, _ = fn
        fn_line_end = y / im_h
        y0 = fn_line_end * page.height
        return y0, y1
    return y1, None
