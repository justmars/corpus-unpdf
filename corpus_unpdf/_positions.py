from pathlib import Path
from typing import NamedTuple

import cv2
from start_ocr import (
    get_contours,
    get_pages_and_imgs,
    get_reverse_pages_and_imgs,
    is_match_text,
)

from ._markers import PositionDecisionCategoryWriter, PositionNotice

ORDERED = "so ordered"
AUTHORITY = "by authority of the court"


def get_start_page_pos(
    path: Path,
) -> tuple[int, PositionNotice | PositionDecisionCategoryWriter | None] | None:
    """The actual start of content depends on either the detection of a
    `Notice` or a `Category`

    This requires searching the page from start to finish, via
    `start_ocr.get_pages_and_imgs()`

    Examples:
        >>> x = Path().cwd() / "tests" / "data" / "notice.pdf"
        >>> res = get_start_page_pos(x)
        >>> type(res[0])
        <class 'int'>
        >>> res[0]
        0
        >>> type(res[1])
        <class 'corpus_unpdf._markers.PositionNotice'>

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


def get_end_page_pos(path: Path) -> tuple[int, int] | None:
    """The actual end of content depends on either two pieces of text:
    the `Ordered` clause or `By Authority of the Court`

    This requires searching the page in reverse, via
    `get_reverse_pages_and_imgs()` since the above pieces of text
    indicate the end of the content.

    Examples:
        >>> from pdfplumber.page import Page
        >>> from pathlib import Path
        >>> import pdfplumber
        >>> x = Path().cwd() / "tests" / "data" / "notice.pdf"
        >>> get_end_page_pos(x) # page 5, y-axis 80.88
        (5, 80.88)

    Also see snippets for debugging:

    ```py
    debug with print(f"{x=}, {y=}, {w=}, {h=}, {y_pos=} {candidate=}")
    cv2.rectangle(im, (x,y), (x+w, y+h), (36, 255, 12), 3) # for each mark
    cv2.imwrite("temp/sample_boxes.png", im); see cv2.rectangle # end of forloop
    ```

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
            sliced_im = im[y : y + h, x : x + w]
            output = page.page_number, (y / im_h) * page.height
            if h < 100:
                if x < MIDPOINT:
                    if is_match_text(
                        sliced_im=sliced_im,
                        text_to_match=ORDERED,
                        likelihood=0.4,
                    ):
                        page.pdf.close()
                        return output
                elif x > MIDPOINT:
                    if is_match_text(
                        sliced_im=sliced_im,
                        text_to_match=AUTHORITY,
                        likelihood=0.4,
                    ):
                        page.pdf.close()
                        return output
    return None


class PositionMeta(NamedTuple):
    """Metadata required to determine the true start and end pages of a given pdf Path.  Although in a collection of pages
    there is a logical start and end page, i.e. page 1 and the final page of a document, in Court documents this sometimes
    does not correspond to the actual start and end of the content.

    Field | Type | Description
    --:|:--:|:--
    `start_index` | int | The zero-based integer `x`, i.e. get specific `pdfplumber.pages[x]`
    `start_page_num` | int | The 1-based integer to describe human-readable page number signifying the true content start
    `start_indicator` | [PositionDecisionCategoryWriter][decision-category-writer] or [PositionNotice][notice] | Marking the start of the content proper
    `end_page_num` | int | The 1-based integer to describe human-readable page number signifying the true content end
    `end_page_pos` | float, int | _y-axis_ position in the `end_page_num`
    """  # noqa: E501

    start_index: int
    start_indicator: PositionDecisionCategoryWriter | PositionNotice
    start_page_num: int
    end_page_num: int
    end_page_pos: float | int

    @classmethod
    def prep(cls, path: Path):
        if not (starter := get_start_page_pos(path)):
            raise Exception("Could not detect start of content.")

        index, start_indicator = starter
        if not start_indicator:
            raise Exception("Could not detect start indicator.")

        ender = get_end_page_pos(path)
        if not ender:
            raise Exception("Could not detect end of content.")
        end_page_num, end_page_pos = ender

        return cls(
            start_index=index,
            start_page_num=index + 1,
            start_indicator=start_indicator,
            end_page_num=end_page_num,
            end_page_pos=end_page_pos,
        )
