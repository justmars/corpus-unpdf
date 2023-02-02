import cv2

from corpus_unpdf.images.contours.resources import get_contours


def get_footnote_coordinates(img: cv2.Mat) -> tuple[int, int, int, int] | None:
    """The footnote line; since we know full image's shape, we can extract max height,
    then use this as the denominator (e.g. 3900) and the matching line described
    in boundingRect as the numerator.

    Args:
        img (cv2.Mat): The open CV image

    Returns:
        float | None: percentage (e.g. ~0.893) of the y-axis
    """

    im_h, _, _ = img.shape
    for c in get_contours(img, (50, 10)):
        x, y, w, h = cv2.boundingRect(c)
        if w > 400 and y > im_h / 2 and h < 40:
            return x, y, w, h
    return None
