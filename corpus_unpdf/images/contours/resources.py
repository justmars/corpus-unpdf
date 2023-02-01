import cv2

def get_contours(img: cv2.Mat, rectangle_size: tuple[int, int]):
    """Generally follows the strategy outlined here:

    1. [Youtube video](https://www.youtube.com/watch?v=ZeCRe9sNFwk&list=PL2VXyKi-KpYuTAZz__9KVl1jQz74bDG7i&index=11)
    2. [Stack Overflow answer](https://stackoverflow.com/a/57262099)

    The structuring element used will be a rectangle of dimensions
    specified in `rectangle_size`. After dilating the image,
    the contours can be enumerated for further processing and
    matching, e.g. after the image is transformed, can find
    which lines appear in the center or in the top right quadrant, etc.

    Args:
        img (cv2.Mat): The opencv formatted image
        rectangle_size (tuple[int, int]): The width and height to morph the characters

    Returns:
        _type_: The contours found based on the specified structuring element
    """ # noqa: E501
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (7, 7), 0)
    thresh = cv2.threshold(
        blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )[1]
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, rectangle_size)
    dilate = cv2.dilate(thresh, kernel, iterations=1)
    cv2.imwrite("temp/sample_dilated.png", dilate)
    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    return sorted(cnts, key=lambda x: cv2.boundingRect(x)[1])
