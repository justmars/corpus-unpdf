from collections.abc import Iterator
from pathlib import Path

import pdfplumber
from PIL import Image


def get_img(pdfpath: str | Path, pagenum: int) -> Image.Image:
    """Extract from `pdfpath` the `PIL`-based image represented
    by the `pagenum` of the file.

    Args:
        pdfpath (str | Path): Source of the PDF to examine
        pagenum (int): The page number of the PDF

    Raises:
        Exception: PIL not generated.

    Returns:
        Image.Image: Image represented by the pagenum of the file.
    """
    pdf = pdfplumber.open(pdfpath)
    page = pdf.pages[pagenum]
    img = page.to_image(resolution=300)
    if isinstance(img.original, Image.Image):
        return img.original
    raise Exception("Could not get PIL-formatted image.")


def get_imgs(pdfpath: Path) -> Iterator[Image.Image]:
    """Extract from `pdfpath` the `PIL`-based images of all the pages
    of the file.

    Args:
        pdfpath (Path): Source of the PDF to examine

    Yields:
        Iterator[Image.Image]: Image of each page found in the file.
    """
    pdf = pdfplumber.open(pdfpath)
    print(f"Pages detected: {len(pdf.pages)}")
    for page in pdf.pages:
        img = page.to_image(resolution=300)
        if isinstance(img.original, Image.Image):
            yield img.original
