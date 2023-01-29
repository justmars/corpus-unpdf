from PIL import Image

from corpus_unpdf import extract_blocks, extract_page_lines


def test_blocks_pdf_page_1(generic_pdf):
    page1 = [blk for blk in extract_blocks(generic_pdf) if blk["page"] == 1]
    assert page1 == [
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
            "text": "                              l\\epublic of tbe ~bilippines Qtourt ~upreme Jr[anila ",  # noqa: E501
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
            "text": "               ATTY. AURORA P. SAN GLAY,         A.M. No. P-14-3182 ",  # noqa: E501
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
            "text": "                                                 Present: ",
        },
        {"page": 1, "counter": 0, "line": 20, "text": ""},
        {
            "page": 1,
            "counter": 0,
            "line": 21,
            "text": "                                                 CARPIO, J., Chairperson, BERSAMIN,* ",  # noqa: E501
        },
        {"page": 1, "counter": 0, "line": 22, "text": ""},
        {"page": 1, "counter": 0, "line": 23, "text": ""},
        {
            "page": 1,
            "counter": 0,
            "line": 24,
            "text": "                         - versus -              DEL CASTILLO, MENDOZA, and LEONEN,JJ. ",  # noqa: E501
        },
        {"page": 1, "counter": 0, "line": 25, "text": ""},
        {"page": 1, "counter": 0, "line": 26, "text": ""},
        {"page": 1, "counter": 0, "line": 27, "text": ""},
        {"page": 1, "counter": 0, "line": 28, "text": ""},
        {
            "page": 1,
            "counter": 0,
            "line": 29,
            "text": "               EDUARDO E. PADUA II, Sheriff IV, Regional Trial Court, Branch 29, San Fernando City, La Union, ",  # noqa: E501
        },
        {"page": 1, "counter": 0, "line": 30, "text": ""},
        {
            "page": 1,
            "counter": 0,
            "line": 31,
            "text": "                                                  Promulgated: ",
        },
        {
            "page": 1,
            "counter": 0,
            "line": 32,
            "text": '                                                     · O"J · JUl ',  # noqa: E501
        },
        {
            "page": 1,
            "counter": 0,
            "line": 33,
            "text": "                               Respondent.                    2D1~~Kt., -",  # noqa: E501
        },
        {
            "page": 1,
            "counter": 0,
            "line": 34,
            "text": "               x----------------------------------------------!~ ~~ ",  # noqa: E501
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
            "text": "                    This is an administrative complaint1 for simple neglect of duty filed by ",  # noqa: E501
        },
        {
            "page": 1,
            "counter": 0,
            "line": 47,
            "text": "               complainant  Atty.  Aurora  P.  Sanglay  (Atty.  Sanglay)  against  respondent ",  # noqa: E501
        },
        {"page": 1, "counter": 0, "line": 48, "text": ""},
        {
            "page": 1,
            "counter": 0,
            "line": 49,
            "text": "               Eduardo  E.  Padua  II  (Padua),  Sheriff IV,  Regional  Trial  Court  (RTC), ",  # noqa: E501
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
            "text": "                    On 13 May 2009, Atty. Sanglay filed with the RTC a motion2 for the ",  # noqa: E501
        },
        {"page": 1, "counter": 0, "line": 56, "text": ""},
        {
            "page": 1,
            "counter": 0,
            "line": 57,
            "text": "               issuance of a writ of execution in Civil Case No. 6031.  In its 29 May 2009 ",  # noqa: E501
        },
        {
            "page": 1,
            "counter": 0,
            "line": 58,
            "text": '               Order, 3 the RTC granted the motion and issued a writ4 of execution, dated 8 June 2009, ordering Padua "to execute the x x x dispositive portion of the ',  # noqa: E501
        },
        {"page": 1, "counter": 0, "line": 59, "text": ""},
        {"page": 1, "counter": 0, "line": 60, "text": ""},
        {"page": 1, "counter": 0, "line": 61, "text": ""},
        {
            "page": 1,
            "counter": 0,
            "line": 62,
            "text": "                   Designated acting member per Special Order No. 2079 dated 29 June 2015. Rollo, pp. 1-4. Id. at 5-6. ",  # noqa: E501
        },
        {
            "page": 1,
            "counter": 0,
            "line": 63,
            "text": "                                                                      ~ ",  # noqa: E501
        },
        {
            "page": 1,
            "counter": 0,
            "line": 64,
            "text": "                   Id. at 7.  Penned by Judge Robert T. Cawed. ",
        },
        {
            "page": 1,
            "counter": 0,
            "line": 65,
            "text": "                   Id. at 16.",
        },
    ]


def test_img_made(page1_generic):
    assert isinstance(page1_generic, Image.Image)


def test_lines_from_img_page_1(page1_generic, keys_per_line):
    lines = list(extract_page_lines(1, page1_generic))
    texts = [line["text"] for line in lines]
    assert len(lines) == 16
    assert isinstance(lines[0], dict)
    assert all(key in lines[0].keys() for key in keys_per_line)
    assert texts == [
        "Resolution 2 A.M. No. P-14-3182",
        (
            "Decision and make a return of [his] proceeding unto [the] Court"
            " within thirty (30) days from the date of receipt [of the writ]"
            " and every thirty (30) days thereafter until [the] Writ shall"
            ' have been fully satisfied."'
        ),
        (
            "Padua failed to make reports as ordered. On 9 March 2010, Atty."
            " Sanglay filed with the RTC a motion® to direct Padua to enforce"
            " the writ of execution and render a report. Because of Padua's"
            " inaction, Atty. Sanglay filed with the RTC two more motions"
            " dated 4 July 2010' and 20 January 2011."
        ),
        (
            "On 10 May 2011, Padua made a partial report.' Padua failed to"
            " make any other report. Hence, the present complaint. In its 1st"
            " Indorsement'® dated 29 July 2011, the Office of the Court"
            " Administrator (OCA) directed Padua to comment on the complaint."
            " Padua submitted his comment'' dated 24 August 2011."
        ),
        "OCA's Report and Recommendations",
        (
            'In its Report!" dated 4 October 2013, the OCA found Padua guilty'
            " of simple neglect of duty and recommended that the complaint be"
            " re-docketed as a regular administrative matter and that Padua be"
            " fined P5,000. The OCA held that:"
        ),
        (
            "The records of the case clearly support the allegation of neglect"
            " of duty against respondent Sheriff Padua. Complainant Sanglay's"
            " motion for issuance of a writ of execution was approved by the"
            " court on 29 May 2009. She subsequently filed two (2) other"
            " motions, dated 4 March 2010 and 4 July 2010, reiterating her"
            " request for the enforcement of the writ. Respondent Sheriff"
            " Padua did not file any report on the status of the writ until 17"
            " May 2011 or almost two (2) years after the court directed him to"
            " enforce the same. The report, in fact, was submitted by"
            " respondent Sheriff Padua only after the filing of the instant"
            " administrative complaint against him."
        ),
        "XXXX",
        (
            "Under Rule 10, Section 46, paragraph (d) of the Revised Rules on"
            " Administrative Cases in the Civil Service, promulgated on 18"
            " November 2011, simple neglect of duty is classified as a less"
            " grave offense which carries the penalty of suspension for one"
            " (1) month and one (1) day to six (6) months for the first"
            " offense and dismissal for the second offense. However, under"
            " Section 48 of the same rules, it is provided that in the"
            " determination of the penalties to be imposed, mitigating"
            " circumstances"
        ),
        "Id. at 8-9.",
        "Id. at 10-11.",
        "Id. at 12-13.",
        "Id. at 17.",
        (
            "Id. at 18. Signed by Court Administrator Jose Midas P. Marquez,"
            " Deputy Court Administrator Raul B. Villanueva and OCA Chief of"
            " Legal Office Wilhelmina D. Geronga."
        ),
        "Id. at 20-21.",
        "Id. at 23-25.",
    ]
