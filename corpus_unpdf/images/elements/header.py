import cv2
from pdfplumber.page import Page

from corpus_unpdf.images.contours.resources import get_contours


def get_header_coordinates(img: cv2.Mat) -> tuple[int, int, int, int] | None:
    im_h, im_w, _ = img.shape
    contours = get_contours(img, (50, 50))
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if x < im_w / 2 and y <= im_h * 0.25 and w > 200 and h < 100:
            return x, y, w, h
    return None


def get_header_terminal(im: cv2.Mat, page: Page) -> float | None:
    im_h, _, _ = im.shape
    hd = get_header_coordinates(im)
    if hd:
        _, y, _, h = hd
        header_end = (y + h) / im_h
        terminal = header_end * page.height
        return terminal
    return None
