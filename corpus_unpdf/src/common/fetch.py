from collections.abc import Iterator
from pathlib import Path

import cv2
import numpy
import pdfplumber

from pdfplumber.page import Page
from PIL import Image


import httpx
from sqlite_utils import Database
from sqlite_utils.db import NotFoundError

SC_BASE_URL = "https://sc.judiciary.gov.ph"


def get_page_and_img(pdfpath: str | Path, index: int) -> tuple[Page, cv2.Mat]:
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
    """Start from the end to get to the first page."""
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


def get_sc_pdf_from_id(dbpath: Path, id: int) -> Path:
    db = Database(dbpath)
    try:
        record = db["db_tbl_sc_web_decisions"].get(28688)  # type: ignore
    except NotFoundError:
        raise Exception(f"Bad {id=}")
    res = httpx.get(f"{SC_BASE_URL}{record['pdf']}")
    target_file = Path().cwd() / "temp" / "temp.pdf"
    target_file.write_bytes(res.content)
    return target_file
