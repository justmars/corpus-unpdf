import pytest
from PIL import Image

from corpus_unpdf import extract_page_lines, get_img


@pytest.fixture
def generic_pdf(shared_datadir) -> dict:
    return shared_datadir / "data_generic.pdf"


def test_img_made(generic_pdf):
    assert isinstance(get_img(generic_pdf, 1), Image.Image)


def test_each_line_content_from_img(generic_pdf):
    img = get_img(generic_pdf, 1)
    lines = extract_page_lines(1, img)
    line = next(lines)
    assert isinstance(line, dict)
    assert all(
        key in line.keys()
        for key in [
            "layout",
            "page",
            "pos",
            "text",
            "decision_type",
            "partial_docket",
            "date_found",
        ]
    )
