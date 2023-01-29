from collections.abc import Iterator
from pathlib import Path
from typing import Any

import cv2
import numpy
import pytesseract
from PIL import Image

from .pdf_img import get_imgs
from .pdf_layout import PageLayout

ROI = "temp/roi.png"
COLOR_GREEN = (36, 255, 12)

# Top of the page to the main content portion
HEADER_TOP = 350

# See structure to contour
WIDTH_HEIGHT = (50, 10)

# See footnote marker in slice_image
LINE_INDICATOR_HEIGHT = 20
LINE_INDICATOR_WIDTH = 400


def extract_slices(img: cv2.Mat, base_img: cv2.Mat):
    """Changes to the image to delinate, specifically find
    footnote lines with long widths and short heights"""
    im_h, im_w, _ = img.shape
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (7, 7), 0)
    thresh = cv2.threshold(
        blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )[1]
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, WIDTH_HEIGHT)
    dilate = cv2.dilate(thresh, kernel, iterations=1)
    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    contours = sorted(cnts, key=lambda x: cv2.boundingRect(x)[1])
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if w > LINE_INDICATOR_WIDTH and h < LINE_INDICATOR_HEIGHT:
            header = base_img[0:HEADER_TOP, 0 : x + im_w]
            body = base_img[HEADER_TOP : y + h, 0 : x + im_w]
            annex = base_img[y + h : im_h, 0 : x + im_w]
            return (header, body, annex)
    return None


def extract_page_lines(
    page_num: int, img: Image.Image
) -> Iterator[dict[str, Any]]:
    """Given a page, extract layout of it (if possible), then
    for each layout, get contextualized lines.

    Args:
        page_num (int): _description_
        img (Image.Image): _description_

    Yields:
        Iterator[dict[str, Any]]: Lines of the pdf represented in dict format.
    """
    print(f"Extracting {page_num=}")
    opencvImage = cv2.cvtColor(numpy.array(img), cv2.COLOR_RGB2BGR)
    im_h, im_w, im_d = opencvImage.shape
    base = opencvImage.copy()
    if slices := extract_slices(base, opencvImage):
        yield from PageLayout.Header.get_texts(
            page_num=page_num,
            text=pytesseract.image_to_string(slices[0]),
        )
        yield from PageLayout.Body.get_texts(
            page_num=page_num,
            text=pytesseract.image_to_string(slices[1]),
        )
        yield from PageLayout.Annex.get_texts(
            page_num=page_num,
            text=pytesseract.image_to_string(slices[2]),
        )
    else:
        sans_header = base[HEADER_TOP:im_h, 0:im_w]
        yield from PageLayout.Body.get_texts(
            page_num=page_num,
            text=pytesseract.image_to_string(sans_header),
        )


def extract_lines_from_pdf(pdf_file_path: Path) -> Iterator[dict[str, Any]]:
    """Given a `pdf_file_path`, get contextualized lines that
    specify

    Args:
        pdf_file_path (Path): Path to the image.

    Yields:
        Iterator[dict[str, Any]]: Each line's layout category, page number,
            and actual text deciphered from the pdf.
    """
    pil_formatted_imgs = get_imgs(pdf_file_path)
    for num, img in enumerate(pil_formatted_imgs, start=1):
        yield from extract_page_lines(num, img)
