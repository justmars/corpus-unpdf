from PIL import Image

from corpus_unpdf import extract_blocks, extract_page_lines


def test_not_working_blocks_pdf_page_1(limited_pdf):
    """Note: Can't parse some PDFs via pdfplumber, used in `extract_blocks()`
    """
    assert not [blk for blk in extract_blocks(limited_pdf) if blk["page"] == 1]


def test_img_made_limited(page1_limited):
    assert isinstance(page1_limited, Image.Image)


def test_lines_from_img_page_1_limited(page1_limited, keys_per_line):
    lines = list(extract_page_lines(1, page1_limited))
    assert len(lines) == 7
    assert isinstance(lines[0], dict)
    assert all(key in lines[0].keys() for key in keys_per_line)
    assert [line["text"] for line in lines] == [
        "Resolution 2. G.R. No. 254838 January 17, 2023",
        (  # noqa: E501
            'Petitioner contends that the period of her detention is "longer'
            " than any other accused similarly charged with the offense of"
            ' plunder."*® She cites the periods of detention of the following:'
            " (1) Former President Gloria Macapagal- Arroyo, who was detained"
            " for a period of 1,387 days prior to her acquittal;? (2) Senator"
            ' Ramon "Bong" Revilla, Jr., who was detained for 1,643 days prior'
            " to his acquittal;'° (3) Former Senator Juan Ponce Enrile, one"
            " of her co-accused, who was detained for 413 days and released on"
            ' bail;!! and (5) Former Senator Jose Pimentel "Jinggoy" Ejercito,'
            " Jr, who was detained for 1,188 days and released on bail.'!*"
            " Thus, petitioner claims that she is entitled to a writ of habeas"
            " corpus and should be discharged from prison by reason of delay"
            " and alleged violation of her constitutional right to speedy"
            " trial.!"
        ),
        (  # noqa: E501
            "Petitioner states that she has filed several petitions before"
            " this Court for release from detention on various and multiple"
            " grounds, but to no avail.'* Thus, she is consequently"
            ' constrained to invoke "the ancient but well- established remedy'
            " of Habeas Corpus Act of 1679, s. 6 against deprivation of"
            ' liberty, specifically on the ground of delay in trial x x x."'
        ),
        (  # noqa: E501
            "In a Notice'® dated January 27, 2021, this Court directed the"
            " Director of the Taguig City Jail Female Dormitory to submit a"
            " return of the writ.'\" All respondents were likewise directed to"
            ' comment on the Petition."®'
        ),
        (  # noqa: E501
            'The Office of the Solicitor General (OSG), through its Comment"'
            " dated March 30, 2021, argues that petitioner is not entitled to"
            ' a writ of habeas corpus because she was "detained pursuant to an'
            " Information charging her with plunder and the warrant of arrest"
            ' issued against her."*° The OSG likewise argues that there was no'
            " delay in trial attributable to either the prosecution or the"
            ' Sandiganbayan."!'
        ),
        (  # noqa: E501
            "The Jail Warden of the Taguig City Jail Female Dormitory, JCINSP"
            " Wena Fe P. Dalagan (Jail Warden), submitted the Return of the"
            ' Writ of Habeas Corpus" dated March 24, 2021 (Return). The Return'
            " provides:"
        ),
        "- over - 281-A",
    ]
