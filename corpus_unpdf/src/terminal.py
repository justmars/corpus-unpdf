import re
from pathlib import Path

import cv2
import pytesseract

from .common import get_contours, get_reverse_pages_and_imgs

ORDERED = re.compile(r"so\s+ordered.*", re.I)
BY_AUTHORITY = re.compile(r"by\s+authority\s+of.*", re.I)


def get_endpageline(target: Path) -> tuple[int, int] | None:
    for page, im in get_reverse_pages_and_imgs(target):
        im_h, im_w, _ = im.shape
        num = page.page_number
        MIDPOINT = im_w / 2
        for cnt in get_contours(im, (30, 30)):
            x, y, w, h = cv2.boundingRect(cnt)
            if h < 100:
                sliced = im[y : y + h, x : x + w]
                y_pos = (y / im_h) * page.height
                if x < MIDPOINT:
                    candidate = pytesseract.image_to_string(sliced).strip()
                    if ORDERED.search(candidate):
                        print(f"{x=}, {y=}, {w=}, {h=}, {candidate=}")
                        # cv2.rectangle(im, (x,y), (x+w, y+h), (36, 255, 12), 3)
                        return num, y_pos
                if x > MIDPOINT - 100:
                    candidate = pytesseract.image_to_string(sliced).strip()
                    if BY_AUTHORITY.search(candidate):
                        print(f"{x=}, {y=}, {w=}, {h=}, {candidate=}")
                        return num, y_pos
    # cv2.imwrite("temp/sample_boxes.png", im); see cv2.rectangle
    return None