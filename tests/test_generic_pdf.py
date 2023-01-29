from PIL import Image

from corpus_unpdf import extract_blocks, extract_page_lines


def test_img_made(page1_generic):
    assert isinstance(page1_generic, Image.Image)


def test_lines_from_img_page_1(page1_generic, keys_per_line):
    """Discrepancy of results of the lines in testing."""
    lines = list(extract_page_lines(1, page1_generic))
    assert len(lines) == 16
    assert isinstance(lines[0], dict)
    assert all(key in lines[0].keys() for key in keys_per_line)


def test_blocks_pdf_page_1(generic_pdf):
    assert [bk for bk in extract_blocks(generic_pdf) if bk["page"] == 1] == [
        {"page": 1, "counter": 0, "line": 0, "text": "pV "},
        {"page": 1, "counter": 0, "line": 1, "text": ""},
        {"page": 1, "counter": 0, "line": 2, "text": ""},
        {"page": 1, "counter": 0, "line": 3, "text": ""},
        {"page": 1, "counter": 0, "line": 4, "text": ""},
        {"page": 1, "counter": 0, "line": 5, "text": ""},
        {"page": 1, "counter": 0, "line": 6, "text": ""},
        {
            "page": 1,
            "counter": 0,
            "line": 7,
            "text": (  # noqa: E501
                "                              l\\epublic of tbe ~bilippines"
                " Qtourt ~upreme Jr[anila "
            ),
        },
        {"page": 1, "counter": 0, "line": 8, "text": ""},
        {"page": 1, "counter": 0, "line": 9, "text": ""},
        {"page": 1, "counter": 0, "line": 10, "text": ""},
        {"page": 1, "counter": 0, "line": 11, "text": ""},
        {"page": 1, "counter": 0, "line": 12, "text": ""},
        {
            "page": 1,
            "counter": 0,
            "line": 13,
            "text": "                                    SECOND DIVISION ",
        },
        {"page": 1, "counter": 0, "line": 14, "text": ""},
        {"page": 1, "counter": 0, "line": 15, "text": ""},
        {
            "page": 1,
            "counter": 0,
            "line": 16,
            "text": (  # noqa: E501
                "               ATTY. AURORA P. SAN GLAY,         A.M. No."
                " P-14-3182 "
            ),
        },
        {"page": 1, "counter": 0, "line": 17, "text": ""},
        {
            "page": 1,
            "counter": 0,
            "line": 18,
            "text": "                               Complainant, ",
        },
        {
            "page": 1,
            "counter": 0,
            "line": 19,
            "text": (
                "                                                 Present: "
            ),
        },
        {"page": 1, "counter": 0, "line": 20, "text": ""},
        {
            "page": 1,
            "counter": 0,
            "line": 21,
            "text": (  # noqa: E501
                "                                                 CARPIO, J.,"
                " Chairperson, BERSAMIN,* "
            ),
        },
        {"page": 1, "counter": 0, "line": 22, "text": ""},
        {"page": 1, "counter": 0, "line": 23, "text": ""},
        {
            "page": 1,
            "counter": 0,
            "line": 24,
            "text": (  # noqa: E501
                "                         - versus -              DEL"
                " CASTILLO, MENDOZA, and LEONEN,JJ. "
            ),
        },
        {"page": 1, "counter": 0, "line": 25, "text": ""},
        {"page": 1, "counter": 0, "line": 26, "text": ""},
        {"page": 1, "counter": 0, "line": 27, "text": ""},
        {"page": 1, "counter": 0, "line": 28, "text": ""},
        {
            "page": 1,
            "counter": 0,
            "line": 29,
            "text": (  # noqa: E501
                "               EDUARDO E. PADUA II, Sheriff IV, Regional"
                " Trial Court, Branch 29, San Fernando City, La Union, "
            ),
        },
        {"page": 1, "counter": 0, "line": 30, "text": ""},
        {
            "page": 1,
            "counter": 0,
            "line": 31,
            "text": (
                "                                                 "
                " Promulgated: "
            ),
        },
        {
            "page": 1,
            "counter": 0,
            "line": 32,
            "text": (  # noqa: E501
                '                                                     · O"J ·'
                " JUl "
            ),
        },
        {
            "page": 1,
            "counter": 0,
            "line": 33,
            "text": (  # noqa: E501
                "                               Respondent.                   "
                " 2D1~~Kt., -"
            ),
        },
        {
            "page": 1,
            "counter": 0,
            "line": 34,
            "text": (  # noqa: E501
                "              "
                " x----------------------------------------------!~ ~~ "
            ),
        },
        {"page": 1, "counter": 0, "line": 35, "text": ""},
        {"page": 1, "counter": 0, "line": 36, "text": ""},
        {
            "page": 1,
            "counter": 0,
            "line": 37,
            "text": "                                    RESOLUTION ",
        },
        {"page": 1, "counter": 0, "line": 38, "text": ""},
        {"page": 1, "counter": 0, "line": 39, "text": ""},
        {"page": 1, "counter": 0, "line": 40, "text": ""},
        {
            "page": 1,
            "counter": 0,
            "line": 41,
            "text": "               CARPIO, J.: ",
        },
        {"page": 1, "counter": 0, "line": 42, "text": ""},
        {"page": 1, "counter": 0, "line": 43, "text": ""},
        {
            "page": 1,
            "counter": 0,
            "line": 44,
            "text": "                                         The Case ",
        },
        {"page": 1, "counter": 0, "line": 45, "text": ""},
        {
            "page": 1,
            "counter": 0,
            "line": 46,
            "text": (  # noqa: E501
                "                    This is an administrative complaint1 for"
                " simple neglect of duty filed by "
            ),
        },
        {
            "page": 1,
            "counter": 0,
            "line": 47,
            "text": (  # noqa: E501
                "               complainant  Atty.  Aurora  P.  Sanglay "
                " (Atty.  Sanglay)  against  respondent "
            ),
        },
        {"page": 1, "counter": 0, "line": 48, "text": ""},
        {
            "page": 1,
            "counter": 0,
            "line": 49,
            "text": (  # noqa: E501
                "               Eduardo  E.  Padua  II  (Padua),  Sheriff IV, "
                " Regional  Trial  Court  (RTC), "
            ),
        },
        {
            "page": 1,
            "counter": 0,
            "line": 50,
            "text": "               Branch 29, San Fernando City, La Union. ",
        },
        {"page": 1, "counter": 0, "line": 51, "text": ""},
        {"page": 1, "counter": 0, "line": 52, "text": ""},
        {
            "page": 1,
            "counter": 0,
            "line": 53,
            "text": "                                        The Facts ",
        },
        {"page": 1, "counter": 0, "line": 54, "text": ""},
        {
            "page": 1,
            "counter": 0,
            "line": 55,
            "text": (  # noqa: E501
                "                    On 13 May 2009, Atty. Sanglay filed with"
                " the RTC a motion2 for the "
            ),
        },
        {"page": 1, "counter": 0, "line": 56, "text": ""},
        {
            "page": 1,
            "counter": 0,
            "line": 57,
            "text": (  # noqa: E501
                "               issuance of a writ of execution in Civil Case"
                " No. 6031.  In its 29 May 2009 "
            ),
        },
        {
            "page": 1,
            "counter": 0,
            "line": 58,
            "text": (  # noqa: E501
                "               Order, 3 the RTC granted the motion and issued"
                ' a writ4 of execution, dated 8 June 2009, ordering Padua "to'
                " execute the x x x dispositive portion of the "
            ),
        },
        {"page": 1, "counter": 0, "line": 59, "text": ""},
        {"page": 1, "counter": 0, "line": 60, "text": ""},
        {"page": 1, "counter": 0, "line": 61, "text": ""},
        {
            "page": 1,
            "counter": 0,
            "line": 62,
            "text": (  # noqa: E501
                "                   Designated acting member per Special Order"
                " No. 2079 dated 29 June 2015. Rollo, pp. 1-4. Id. at 5-6. "
            ),
        },
        {
            "page": 1,
            "counter": 0,
            "line": 63,
            "text": (  # noqa: E501
                "                                                             "
                "         ~ "
            ),
        },
        {
            "page": 1,
            "counter": 0,
            "line": 64,
            "text": (
                "                   Id. at 7.  Penned by Judge Robert T."
                " Cawed. "
            ),
        },
        {
            "page": 1,
            "counter": 0,
            "line": 65,
            "text": "                   Id. at 16.",
        },
    ]
