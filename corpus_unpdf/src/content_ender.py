from pathlib import Path

import cv2

from .common import get_contours, get_reverse_pages_and_imgs, is_match_text


def get_end_page_pos(path: Path) -> tuple[int, int] | None:
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
    ORDERED, AUTHORITY = "so ordered", "by authority of the court"
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
