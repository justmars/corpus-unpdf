import cv2
from pathlib import Path
from .common import get_contours, is_match_text, get_pages_and_imgs
from pdfplumber.page import Page
from .markers import PositionNotice, PositionDecisionCategoryWriter


def get_start_page_pos(
    path: Path,
) -> tuple[
    Page, PositionNotice | PositionDecisionCategoryWriter | None
] | None:
    """Although the collection of pages has a logical start page, this
    _exceptionally_ does not correspond to the actual start of the content.

    The actual start of content depends on either the detection of a
    Notice or a Category

    This requires searching the page from start to finish, via
    `get_pages_and_imgs()`

    Examples:
        >>> from pdfplumber.page import Page
        >>> from pathlib import Path
        >>> import pdfplumber
        >>> x = Path().cwd() / "tests" / "data" / "notice.pdf"
        >>> get_pages_and_imgs(x) # page 5, y-axis 80.88
        (5, 80.88)

    Args:
        path (Path): Path to the PDF file.

    Returns:
        tuple[Page, PositionNotice | PositionDecisionCategoryWriter | None] | None:
            The page number from pdfplumber.pages, the marker found that signifies start
    """
    for page, im in get_pages_and_imgs(path):
        _, im_w, _ = im.shape
        MIDPOINT = im_w / 2
        for cnt in get_contours(im, (30, 30)):
            x, y, w, h = cv2.boundingRect(cnt)
            one_liner = h < 100
            x_start_mid = x < MIDPOINT
            x_end_mid = (x + w) > MIDPOINT
            short_width = 200 < w < 600
            if all([one_liner, x_start_mid, x_end_mid, short_width]):
                cv2.rectangle(im, (x, y), (x + w, y + h), (36, 255, 12), 3)
                sliced = im[y : y + h, x : x + w]
                print(f"{x=}, {y=}, {w=}, {h=}")
                if is_match_text(sliced, "notice"):
                    return page, PositionNotice.extract(im)
                elif is_match_text(sliced, "decision"):
                    return page, PositionDecisionCategoryWriter.extract(im)
                elif is_match_text(sliced, "resolution"):
                    return page, PositionDecisionCategoryWriter.extract(im)
        cv2.imwrite(f"temp/sample_boxes-{page.page_number}.png", im)
    return None
