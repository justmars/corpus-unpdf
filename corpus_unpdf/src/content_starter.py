from pathlib import Path

import cv2

from .common import get_contours, get_pages_and_imgs, is_match_text
from .content_markers import PositionDecisionCategoryWriter, PositionNotice


def get_start_page_pos(
    path: Path,
) -> tuple[int, PositionNotice | PositionDecisionCategoryWriter | None] | None:
    """Although the collection of pages has a logical start page, this
    _exceptionally_ does not correspond to the actual start of the content.

    The actual start of content depends on either the detection of a
    Notice or a Category

    This requires searching the page from start to finish, via
    `get_pages_and_imgs()`

    Examples:
        >>> x = Path().cwd() / "tests" / "data" / "notice.pdf"
        >>> res = get_start_page_pos(x)
        >>> type(res[0])
        <class 'int'>
        >>> res[0]
        0
        >>> type(res[1])
        <class 'corpus_unpdf.src.content_markers.PositionNotice'>

    Args:
        path (Path): Path to the PDF file.

    Returns:
        tuple[int, PositionNotice | PositionDecisionCategoryWriter | None] | None:
            The zero-based index of the page (i.e. 0 = page 1), the marker found that
            signifies start of the content
    """
    for page, im in get_pages_and_imgs(path):
        index = page.page_number - 1  # represents the 0-based index
        _, im_w, _ = im.shape
        MIDPOINT = im_w / 2
        for cnt in get_contours(im, (30, 30)):
            x, y, w, h = cv2.boundingRect(cnt)
            one_liner = h < 100
            x_start_mid = x < MIDPOINT
            x_end_mid = (x + w) > MIDPOINT
            short_width = 200 < w < 800
            if all([one_liner, x_start_mid, x_end_mid, short_width]):
                sliced = im[y : y + h, x : x + w]
                # cv2.rectangle(im, (x, y), (x + w, y + h), (36, 255, 12), 3)
                # print(f"{x=}, {y=}, {w=}, {h=}")
                if is_match_text(sliced, "notice"):
                    return index, PositionNotice.extract(im)
                elif is_match_text(sliced, "decision"):
                    return index, PositionDecisionCategoryWriter.extract(im)
                elif is_match_text(sliced, "resolution"):
                    return index, PositionDecisionCategoryWriter.extract(im)
        # cv2.imwrite(f"temp/sample_boxes-{page.page_number}.png", im)
    return None
