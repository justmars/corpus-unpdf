import cv2
import numpy
from pdfplumber.page import Page

from .common import get_contours


def get_header_docket_coordinates(
    im: numpy.ndarray,
) -> tuple[int, int, int, int] | None:
    """The header represents non-title page content above the main content.

    It usually consists of three items:

    Item | Label | Example
    --:|:--|:--
    1 | Type of decision | `Resolution` or `Decision`
    2 | Page number | 1, 2, 3, etc.
    3 | Docket of the decision involved | GR. 12414, Dec. 1, 2023

    This detects Item (3) which implies that it is the in upper right quarter
    of the document:

    ```py
    x > im_w / 2 # ensures that it is on the right side of the page
    y <= im_h * 0.2 # ensures that it is on the top quarter of the page
    ```

    Item (3) is the only one above that is likely to have a second vertical line,
    hence choosing this as the the typographic bottom for the header makes sense.

    Examples:
        >>> from corpus_unpdf.src import get_page_and_img
        >>> from pathlib import Path
        >>> x = Path().cwd() / "tests" / "data" / "decision.pdf"
        >>> page, im = get_page_and_img(x, 1) # 0 marks the second page
        >>> get_header_docket_coordinates(im)
        (1813, 229, 460, 84)
        >>> page.pdf.close()

    Args:
        im (numpy.ndarray): The full page image

    Returns:
        tuple[int, int, int, int] | None: The coordinates of the docket, if found.
    """
    im_h, im_w, _ = im.shape
    for cnt in get_contours(im, (50, 50)):
        x, y, w, h = cv2.boundingRect(cnt)
        if x > im_w / 2 and y <= im_h * 0.25 and w > 200:
            return x, y, w, h
    return None


def get_header_line(im: numpy.ndarray, page: Page) -> int | float | None:
    """The header represents non-title page content above the main content.

    The terminating header line is a non-visible line that separates the
    decision's header from its main content. We'll use a typographic bottom
    of the [header][docket-coordinates] to signify this line.

    Examples:
        >>> from corpus_unpdf.src import get_page_and_img
        >>> from pathlib import Path
        >>> x = Path().cwd() / "tests" / "data" / "decision.pdf"
        >>> page, im = get_page_and_img(x, 1) # 1 marks the second page
        >>> get_header_line(im, page)
        75.12
        >>> page.pdf.close()

    Args:
        im (numpy.ndarray): The full page image
        page (Page): The pdfplumber page

    Returns:
        float | None: Y-axis point (pdfplumber point) at bottom of header
    """
    im_h, _, _ = im.shape
    if hd := get_header_docket_coordinates(im):
        _, y, _, h = hd
        header_end = (y + h) / im_h
        terminal = header_end * page.height
        return terminal
    return None


def get_page_num(page: Page, header_line: int | float) -> int | None:
    """Get the first matching digit in the header's text. This helps
    deal with decisions having blank pages.

    Examples:
        >>> import pdfplumber
        >>> from pathlib import Path
        >>> from corpus_unpdf.src.common.fetch import get_img_from_page
        >>> x = Path().cwd() / "tests" / "data" / "decision.pdf"
        >>> pdf = pdfplumber.open(x)
        >>> page = pdf.pages[1] # page 2
        >>> im = get_img_from_page(page)
        >>> header_line = get_header_line(im, page)
        >>> get_page_num(page, header_line)
        2
        >>> pdf.close()

    Args:
        page (Page): The pdfplumber page
        header_line (int | float): The value retrieved from `get_header_line()`

    Returns:
        int | None: The page number, if found
    """
    box = (0, 0, page.width, header_line)
    header = page.crop(box, relative=False, strict=True)
    texts = header.extract_text(layout=True, keep_blank_chars=True).split()
    for text in texts:
        if text.isdigit() and len(text) <= 3:
            return int(text)
    return None
