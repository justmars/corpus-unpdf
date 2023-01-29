from PIL import Image

from corpus_unpdf import extract_blocks, extract_page_lines


def test_not_working_blocks_pdf_page_1(limited_pdf):
    """Note: Can't parse some PDFs via pdfplumber, used in `extract_blocks()`
    """
    assert not [blk for blk in extract_blocks(limited_pdf) if blk["page"] == 1]


def test_img_made_limited(page1_limited):
    assert isinstance(page1_limited, Image.Image)


def test_lines_from_img_page_1_limited(page1_limited, keys_per_line):
    """There seems to be discrepancy on the number of lines outputted
    based on the version of imagemagicks used;
    The local client device has `imagemagick-7` installed but
    the item in github workflow appears to use `imagemagick-6`.
    In the local client, the number of lines produced is 7;
    in the worflow: 11.
    """
    lines = list(extract_page_lines(1, page1_limited))
    assert len(lines) in [7, 11]  # read comment
    assert isinstance(lines[0], dict)
    assert all(key in lines[0].keys() for key in keys_per_line)
