import re
from collections.abc import Iterator
from pathlib import Path

import cv2
import numpy
import pdfplumber
import pytesseract
from pdfplumber.page import Page

from .slice import get_contours

ORDERED = re.compile(r"so\s+ordered.*", re.I)
BY_AUTHORITY = re.compile(r"by\s+authority\s+of.*", re.I)


def get_img_from_page(page: Page) -> numpy.ndarray:
    return cv2.cvtColor(
        numpy.array(page.to_image(resolution=300).original), cv2.COLOR_RGB2BGR
    )


def get_page_and_img(
    pdfpath: str | Path, index: int
) -> tuple[Page, numpy.ndarray]:
    """Combines `OpenCV` with `pdfplumber`.

    Examples:
        >>> import numpy
        >>> from pdfplumber.page import Page
        >>> from pathlib import Path
        >>> x = Path().cwd() / "tests" / "data" / "decision.pdf"
        >>> page, im = get_page_and_img(x, 0) # 0 marks the first page
        >>> page.page_number # the first page
        1
        >>> isinstance(page, Page)
        True
        >>> isinstance(im, numpy.ndarray)
        True

    Args:
        pdfpath (str | Path): Path to the PDF file.
        index (int): Zero-based index that determines the page number.

    Returns:
        tuple[Page, numpy.ndarray]: Page identified by `index`  with image of the
            page  (in numpy format) that can be manipulated.
    """
    pdf = pdfplumber.open(pdfpath)
    page = pdf.pages[index]
    img = get_img_from_page(page)
    return page, img


def get_reverse_pages_and_imgs(
    pdfpath: str | Path,
) -> Iterator[tuple[Page, numpy.ndarray]]:
    """Start from the end page to get to the first page
    to determine terminal values.

    Examples:
        >>> from pdfplumber.page import Page
        >>> from pathlib import Path
        >>> import pdfplumber
        >>> x = Path().cwd() / "tests" / "data" / "decision.pdf"
        >>> results = get_reverse_pages_and_imgs(x)
        >>> result = next(results)
        >>> type(result)
        <class 'tuple'>
        >>> isinstance(result[0], Page)
        True
        >>> assert result[0].page_number == len(pdfplumber.open(x).pages) # last first

    Args:
        pdfpath (str | Path): Path to the PDF file.

    Yields:
        Iterator[tuple[Page, numpy.ndarray]]: Pages with respective images
    """
    with pdfplumber.open(pdfpath) as pdf:
        index = len(pdf.pages) - 1
        while True:
            page = pdf.pages[index]
            yield page, get_img_from_page(page)
            if index == 0:
                break
            index -= 1


def get_terminal_page_pos(path: Path) -> tuple[int, int] | None:
    """Although the collection of pages has a logical end page, this
    oftentimes does not correspond to the actual end of the content.

    The actual end of content depends on either two pieces of text:
    the `Ordered` clause or `By Authority of the Court`

    This requires searching the page in reverse, via
    `get_reverse_pages_and_imgs()` since the above pieces of text
    indicate the end of the content.

    Examples:
        >>> from pdfplumber.page import Page
        >>> from pathlib import Path
        >>> import pdfplumber
        >>> x = Path().cwd() / "tests" / "data" / "notice.pdf"
        >>> get_terminal_page_pos(x) # page 5, y-axis 80.88
        (5, 80.88)

    Args:
        path (Path): Path to the PDF file.

    Returns:
        tuple[int, int] | None: The page number from pdfplumber.pages, the Y position
            of that page
    """
    for page, im in get_reverse_pages_and_imgs(path):
        im_h, im_w, _ = im.shape
        MIDPOINT = im_w / 2
        for cnt in get_contours(im, (30, 30)):
            x, y, w, h = cv2.boundingRect(cnt)
            if h < 100:
                sliced = im[y : y + h, x : x + w]
                y_pos = (y / im_h) * page.height
                if x < MIDPOINT:
                    candidate = pytesseract.image_to_string(sliced).strip()
                    if ORDERED.search(candidate):
                        # print(f"{x=}, {y=}, {w=}, {h=}, {candidate=}")
                        # cv2.rectangle(im, (x,y), (x+w, y+h), (36, 255, 12), 3)
                        return page.page_number, y_pos
                if x > MIDPOINT - 100:
                    candidate = pytesseract.image_to_string(sliced).strip()
                    if BY_AUTHORITY.search(candidate):
                        # print(f"{x=}, {y=}, {w=}, {h=}, {candidate=}")
                        # cv2.rectangle(im, (x,y), (x+w, y+h), (36, 255, 12), 3)
                        return page.page_number, y_pos
    # cv2.imwrite("temp/sample_boxes.png", im); see cv2.rectangle
    return None
