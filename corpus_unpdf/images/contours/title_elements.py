import cv2
from .resources import get_contours

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
        x0_in_center_left = im_w / 3 < x < im_w / 2
        x1_in_center_right = (x + w) > (im_w / 2) + 100
        y0_in_top_third = y < im_h / 3
        width_long = w > 200
        height_regular = h > 30
        if all([
            x0_in_center_left,
            x1_in_center_right,
            y0_in_top_third,
            width_long,
            height_regular,
        ]):
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
        if w > 1200:
            return (y + h) / im_h
    return None
