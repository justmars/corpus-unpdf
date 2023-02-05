from collections.abc import Iterator
from pathlib import Path

import cv2
import numpy
import pdfplumber
from pdfplumber.page import Page


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
        >>> page.pdf.close()

    Args:
        pdfpath (str | Path): Path to the PDF file.
        index (int): Zero-based index that determines the page number.

    Returns:
        tuple[Page, numpy.ndarray]: Page identified by `index`  with image of the
            page  (in numpy format) that can be manipulated.
    """
    with pdfplumber.open(pdfpath) as pdf:
        page = pdf.pages[index]
        img = get_img_from_page(page)
        return page, img


def get_pages_and_imgs(
    pdfpath: str | Path,
) -> Iterator[tuple[Page, numpy.ndarray]]:
    """Get the page and images in sequential order.

    Examples:
        >>> from pdfplumber.page import Page
        >>> from pathlib import Path
        >>> import pdfplumber
        >>> x = Path().cwd() / "tests" / "data" / "decision.pdf"
        >>> results = get_pages_and_imgs(x)
        >>> result = next(results)
        >>> type(result)
        <class 'tuple'>
        >>> isinstance(result[0], Page)
        True
        >>> assert result[0].page_number == 1 # first

    Args:
        pdfpath (Page | Path): Path to the PDF file.

    Yields:
        Iterator[tuple[Page, numpy.ndarray]]: Pages with respective images
    """
    with pdfplumber.open(pdfpath) as pdf:
        index = 0
        while index < len(pdf.pages):
            page = pdf.pages[index]
            yield page, get_img_from_page(page)
            index += 1


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
        pdfpath (Page | Path): Path to the PDF file.

    Yields:
        Iterator[tuple[Page, numpy.ndarray]]: Pages with respective images
    """
    with pdfplumber.open(pdfpath) as pdf:
        index = len(pdf.pages) - 1
        while index >= 0:
            page = pdf.pages[index]
            yield page, get_img_from_page(page)
            index -= 1
