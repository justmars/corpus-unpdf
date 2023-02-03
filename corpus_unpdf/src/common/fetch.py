from collections.abc import Iterator
from pathlib import Path

import cv2
import numpy
import pdfplumber
from pdfplumber.page import Page
from PIL import Image


def get_page_and_img(pdfpath: str | Path, index: int) -> tuple[Page, cv2.Mat]:
    """Combine `OpenCV` with `pdfplumber` by using the page
    identified by `index` to generate an image that can be
    manipulated.

    Args:
        pdfpath (str | Path): Path to the PDF file.
        index (int): Zero-based index that determines the page number.

    Returns:
        tuple[Page, cv2.Mat]: _description_
    """
    pdf = pdfplumber.open(pdfpath)
    page = pdf.pages[index]
    img = page.to_image(resolution=300)
    if isinstance(img.original, Image.Image):
        cv2_image = cv2.cvtColor(numpy.array(img.original), cv2.COLOR_RGB2BGR)
        return page, cv2_image
    raise Exception("Could not get CV2-formatted image.")


def get_reverse_pages_and_imgs(
    pdfpath: str | Path,
) -> Iterator[tuple[Page, cv2.Mat]]:
    """Start from the end page to get to the first page. This will
    enable tracking values from the last page first to determine
    the terminal endpoints.
    """
    pdf = pdfplumber.open(pdfpath)
    max_pages = len(pdf.pages)
    index = max_pages - 1
    while True:
        page = pdf.pages[index]
        img = page.to_image(resolution=300)
        if isinstance(img.original, Image.Image):
            cv2_image = cv2.cvtColor(
                numpy.array(img.original), cv2.COLOR_RGB2BGR
            )
            yield page, cv2_image
        if index == 0:
            break
        index -= 1
