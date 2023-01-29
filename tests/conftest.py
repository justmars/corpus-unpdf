import pytest

from corpus_unpdf import get_img


@pytest.fixture
def limited_pdf(shared_datadir) -> dict:
    """Used to demonstrate that `extract_blocks()`
    won't work here but image extraction will."""
    return shared_datadir / "data_limited.pdf"


@pytest.fixture
def page1_limited(limited_pdf):
    return get_img(limited_pdf, 1)


@pytest.fixture
def generic_pdf(shared_datadir) -> dict:
    """Used to demonstrate that `extract_blocks()`
    and image extraction will work here."""
    return shared_datadir / "data_generic.pdf"


@pytest.fixture
def page1_generic(generic_pdf):
    return get_img(generic_pdf, 1)


@pytest.fixture
def keys_per_line():
    return [
        "layout",
        "page",
        "pos",
        "text",
        "decision_type",
        "partial_docket",
        "date_found",
    ]
