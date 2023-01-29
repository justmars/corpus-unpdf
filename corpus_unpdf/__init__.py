__version__ = "0.0.1"

from .blocks.pdf_blocks import extract_blocks
from .images import (
    extract_lines_from_pdf,
    extract_page_lines,
    extract_slices,
    get_img,
    get_imgs,
    set_file,
)
