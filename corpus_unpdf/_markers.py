from enum import Enum
from typing import NamedTuple, Self

import numpy as np
import pytesseract
from pdfplumber.pdf import PDF
from start_ocr import get_img_from_page, get_likelihood_centered_coordinates


class NoticeChoices(Enum):
    NOTICE = "Notice"


class PositionNotice(NamedTuple):
    """When present, signifies issuance by authority of the Court.

    Field | Type | Description
    --:|:--:|:--
    `element` | NoticeChoices | Only a single choice (for now)
    `coordinates` | tuple[int, int, int, int] | The opencv rectangle found in the page where the notice is found
    `position_pct_height` | float | The `y` + height `h` of the `coordinates` over the `im_h` image height; used so the pdfplumber can utilize its cropping mechanism.
    """  # noqa: E501

    element: NoticeChoices
    coordinates: tuple[int, int, int, int]
    position_pct_height: float

    @classmethod
    def extract(cls, im: np.ndarray) -> Self | None:
        im_h, _, _ = im.shape
        for member in NoticeChoices:
            if xywh := get_likelihood_centered_coordinates(im, member.value):
                y, h = xywh[1], xywh[3]
                return cls(
                    element=member,
                    coordinates=xywh,
                    position_pct_height=(y + h) / im_h,
                )
        return None


class CourtCompositionChoices(Enum):
    """How Philippine Supreme Court sits. At present, this includes four options: en banc + 3 divisions. TODO: Might need to add cases for _special_ divisions."""  # noqa: E501

    ENBANC = "En Banc"
    DIV1 = "First Division"
    DIV2 = "Second Division"
    DIV3 = "Third Division"


class PositionCourtComposition(NamedTuple):
    """Should be present as top centered element in the first page of a Decision PDF file.

    Field | Type | Description
    --:|:--:|:--
    `element` | [CourtCompositionChoices][composition-choices] | Presently four choices
    `coordinates` | tuple[int, int, int, int] | The opencv rectangle found in the page where the composition is found
    `composition_pct_height` | float | The `y` + height `h` of the `coordinates` over the `im_h` image height; used so the pdfplumber can utilize its cropping mechanism.
    """  # noqa: E501

    element: CourtCompositionChoices
    coordinates: tuple[int, int, int, int]
    composition_pct_height: float

    @classmethod
    def extract(cls, im: np.ndarray) -> Self | None:
        im_h, _, _ = im.shape
        for member in CourtCompositionChoices:
            if xywh := get_likelihood_centered_coordinates(im, member.value):
                y, h = xywh[1], xywh[3]
                return cls(
                    element=member,
                    coordinates=xywh,
                    composition_pct_height=(y + h) / im_h,
                )
        return None

    @classmethod
    def from_pdf(cls, pdf: PDF) -> Self:
        page_one_im = get_img_from_page(pdf.pages[0])
        court_composition = cls.extract(page_one_im)
        if not court_composition:
            raise Exception("Could not detect court compositon in page 1.")
        return court_composition


class DecisionCategoryChoices(Enum):
    """The classification of a decision issued by the Supreme Court, i.e.
    a decision or a resolution."""

    CASO = "Decision"
    RESO = "Resolution"


class PositionDecisionCategoryWriter(NamedTuple):
    """Should be present as top centered element in the first page of a Decision PDF file.

    Field | Type | Description
    --:|:--:|:--
    `element` | [DecisionCategoryChoices][category-choices] | Presently four choices
    `coordinates` | tuple[int, int, int, int] | The opencv rectangle found in the page where the `composition` element is found
    `writer` | str | The string found indicating the name of the writer
    `category_pct_height` | float | The `y` + height `h` of the `coordinates` over the `im_h` image height; used so the pdfplumber can utilize its cropping mechanism.
    `writer_pct_height` | float | The writer's coordinates are found below the category coordinates. This can then be used to signify the anchoring start of the document.
    """  # noqa: E501

    element: DecisionCategoryChoices
    coordinates: tuple[int, int, int, int]
    writer: str
    category_pct_height: float
    writer_pct_height: float

    @classmethod
    def extract(cls, im: np.ndarray) -> Self | None:
        im_h, _, _ = im.shape
        for member in DecisionCategoryChoices:
            if xywh := get_likelihood_centered_coordinates(im, member.value):
                _, y, _, h = xywh
                y0, y1 = y + h, y + 270
                writer_box = im[y0:y1]
                writer = pytesseract.image_to_string(writer_box).strip()
                return cls(
                    element=member,
                    coordinates=xywh,
                    writer=writer,
                    category_pct_height=y / im_h,
                    writer_pct_height=y1 / im_h,
                )
        return None
