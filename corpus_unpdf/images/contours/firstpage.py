import cv2
from .resources import get_contours, get_page_and_img
from .footnotes import get_pos_footnote_start
from typing import NamedTuple, Self
import pytesseract
from pathlib import Path
from pdfplumber.page import CroppedPage, Page


def looks_centric(im_w, im_h, x, y, w, h) -> bool:
    x0_in_center_left = im_w / 3 < x < im_w / 2
    x1_in_center_right = (x + w) > (im_w / 2) + 100
    y0_in_top_third = y < im_h / 3
    width_long = w > 200
    height_regular = h > 30
    return all(
        [
            x0_in_center_left,
            x1_in_center_right,
            y0_in_top_third,
            width_long,
            height_regular,
        ]
    )


def get_pos_notice_end(img: cv2.Mat) -> float | None:
    im_h, im_w, _ = img.shape
    limited = []
    for c in get_contours(img, (100, 30)):
        x, y, w, h = cv2.boundingRect(c)
        if looks_centric(im_w, im_h, x, y, w, h):
            limited.append((x, y, w, h))
    if limited:
        x, y, w, h = limited[-1]
        sliced_image = img[y : y + h, x : x + w]
        text_in_position = pytesseract.image_to_string(sliced_image)
        if "notice" in text_in_position.casefold():
            return (y + h) / im_h
    return None


def get_pos_title_start(img: cv2.Mat) -> float | None:
    """Get the bottom most title position, usually appears in the first page
    of a decision. This should be able to handle two distinct formats:

    (a) regular Decisions; and
    (b) resolutions which start with the word `Notice`
    """
    im_h, im_w, _ = img.shape
    limited = []
    for c in get_contours(img, (100, 30)):
        x, y, w, h = cv2.boundingRect(c)
        if looks_centric(im_w, im_h, x, y, w, h):
            limited.append((y + h) / im_h)
    if limited:
        return max(limited)
    return None


def get_pos_title_end(img: cv2.Mat) -> float | None:
    """The start decision line of non-resolutions; since we know full image's shape,
    we can extract max height, then use this as the denominator (e.g. 3900) and the
    matching line described in boundingRect as the numerator.

    Args:
        img (cv2.Mat): The open CV image; should be the first page of the PDF

    Returns:
        float | None: percentage (e.g. ~0.893) of the y-axis
    """
    im_h, _, _ = img.shape
    for c in get_contours(img, (30, 10)):
        _, y, w, h = cv2.boundingRect(c)
        if y > im_h / 3 and w > 1800 and h > 100:
            return (y + h) / im_h
    return None


class TitlePageHeights(NamedTuple):
    title_start: float | None
    title_end: float | None
    footnote_start: float | None
    notice_end: float | None

    @classmethod
    def set_heights(cls, im: cv2.Mat) -> Self:
        return cls(
            title_start=get_pos_title_start(im),
            title_end=get_pos_title_end(im),
            footnote_start=get_pos_footnote_start(im),
            notice_end=get_pos_notice_end(im),
        )  # type: ignore

    @property
    def is_titled(self) -> bool:
        return all([self.title_start, self.title_end, self.footnote_start])

    @property
    def is_notice(self) -> bool:
        return all([self.notice_end, self.footnote_start])


class StartPage(NamedTuple):
    header: CroppedPage | None
    body: CroppedPage | None
    annex: CroppedPage | None

    @classmethod
    def extract(cls, pdf_path: Path) -> Self | None:
        page, im = get_page_and_img(pdf_path, 0)
        return cls.get_decision(page, im) or cls.get_notice(page, im)

    @classmethod
    def get_notice(cls, page: Page, im: cv2.Mat) -> Self | None:
        # set constants
        x = 70
        w = page.width - 10
        bottom_margin_percent = 0.95

        # determine if page 1 positions exist
        HEIGHTS = TitlePageHeights.set_heights(im)
        if not HEIGHTS.is_notice:
            return None

        # establish cropping boxes
        y_pos_header_end = page.height * HEIGHTS.notice_end  # type: ignore
        y_pos_footnote_start = page.height * HEIGHTS.footnote_start  # type: ignore
        y_pos_footnote_end = page.height * bottom_margin_percent  # type: ignore

        # get slices based on cropping boxes
        slide_body = (x, y_pos_header_end, w, y_pos_footnote_start)
        slide_annex = (x, y_pos_footnote_start, w, y_pos_footnote_end)

        # create the page, with parts cropped
        return cls(
            header=None,
            body=page.crop(slide_body, relative=False, strict=True),
            annex=page.crop(slide_annex, relative=False, strict=True),
        )

    @classmethod
    def get_decision(cls, page: Page, im: cv2.Mat) -> Self | None:
        # set constants
        x = 70
        w = page.width - 10
        bottom_margin_percent = 0.95

        # determine if page 1 positions exist
        HEIGHTS = TitlePageHeights.set_heights(im)
        if not HEIGHTS.is_titled:
            return None

        # establish cropping boxes
        y_pos_header_start = page.height * HEIGHTS.title_start  # type: ignore
        y_pos_header_end = page.height * HEIGHTS.title_end  # type: ignore
        y_pos_footnote_start = page.height * HEIGHTS.footnote_start  # type: ignore
        y_pos_footnote_end = page.height * bottom_margin_percent  # type: ignore

        # get slices based on cropping boxes
        slice_header = (x, y_pos_header_start, w, y_pos_header_end)
        slide_body = (x, y_pos_header_end, w, y_pos_footnote_start)
        slide_annex = (x, y_pos_footnote_start, w, y_pos_footnote_end)

        # create the page, with parts cropped
        return cls(
            header=page.crop(slice_header, relative=False, strict=True),
            body=page.crop(slide_body, relative=False, strict=True),
            annex=page.crop(slide_annex, relative=False, strict=True),
        )
