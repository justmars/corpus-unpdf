import cv2
import numpy
from pdfplumber.page import Page

from .common import get_contours
from .markers import PERCENT_OF_MAX_PAGE


def get_footer_line_coordinates(
    im: numpy.ndarray,
) -> tuple[int, int, int, int] | None:
    """The footer represents content below the main content. This is also
    called the annex of the page.

    This detects a short line in the lower half of the page that has at least a width
    of 400 pixels and a height of less than 40 pixels, indicating a narrow box
    (as dilated by openCV). Text found below this box represents the annex.

    Examples:
        >>> from corpus_unpdf.src import get_page_and_img
        >>> from pathlib import Path
        >>> x = Path().cwd() / "tests" / "data" / "decision.pdf"
        >>> page, im = get_page_and_img(x, 1) # 0 marks the second page
        >>> get_footer_line_coordinates(im)
        (426, 3148, 499, 13)
        >>> page.pdf.close()

    Args:
        im (numpy.ndarray): The full page image

    Returns:
        tuple[int, int, int, int] | None: The coordinates of the footer line, if found.
    """

    im_h, _, _ = im.shape
    for c in get_contours(im, (50, 10)):
        x, y, w, h = cv2.boundingRect(c)
        if w > 400 and y > im_h / 2 and h < 40:
            return x, y, w, h
    return None


def get_annex_y_axis(
    im: numpy.ndarray, page: Page
) -> tuple[float, float | None]:
    """Given an `im`, detect the footnote line of the annex and return
    relevant points in the y-axis as a tuple.

    Scenario | Description | y0 | y1
    :--:|:-- |:--:|:--:
    Footnote line exists | Page contains footnotes | int or float | int or float signifying end of page
    Footnote line absent | Page does not contain footnotes | int or float signifying end of page | `None`

    Args:
        im (numpy.ndarray): the openCV image that may contain a footnote line
        page (Page): the pdfplumber.page.Page based on `im`

    Returns:
        tuple[float, float | None]: The annex line's y-axis (if it exists) and
            The page's end content line
    """  # noqa: E501
    im_h, _, _ = im.shape
    fn = get_footer_line_coordinates(im)
    y1 = PERCENT_OF_MAX_PAGE * page.height
    if fn:
        _, y, _, _ = fn
        fn_line_end = y / im_h
        y0 = fn_line_end * page.height
        return y0, y1
    return y1, None
