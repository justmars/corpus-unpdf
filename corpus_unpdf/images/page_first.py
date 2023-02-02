from dataclasses import dataclass
from pathlib import Path

from pdfplumber.page import CroppedPage

from .contours import PageCut, get_page_and_img
from .elements import (
    CourtCompositionChoices,
    DecisionCategoryChoices,
    PositionCourtComposition,
    PositionDecisionCategoryWriter,
    PositionNotice,
    get_annex_y_axis,
)


@dataclass
class FirstPage:
    header: CroppedPage
    body: CroppedPage
    composition: CourtCompositionChoices
    notice: bool = False
    writer: str | None = None
    category: DecisionCategoryChoices | None = None
    annex: CroppedPage | None = None

    @classmethod
    def extract(cls, path: Path):
        annex = None
        page, im = get_page_and_img(path, 0)
        comp = PositionCourtComposition.extract(im)
        if not comp:
            raise Exception(f"No court composition detected {path=}")

        sliced = {"page": page, "x0": 75, "x1": page.width - 75}
        head = comp.get_y_axis_composition(page)
        fn_start, fn_end = get_annex_y_axis(im, page)
        if fn_start and fn_end:
            annex = PageCut(**sliced, y0=fn_start, y1=fn_end).result

        fields = {"annex": annex, "composition": comp.element}
        if notice := PositionNotice.extract(im):
            y_pos = notice.get_y_pos(page)
            return cls(
                header=PageCut(**sliced, y0=head, y1=y_pos).result,
                body=PageCut(**sliced, y0=y_pos, y1=fn_start).result,
                notice=True,
                **fields,
            )
        elif cat := PositionDecisionCategoryWriter.extract(im):
            cat_pos = cat.get_y_axis_category(page)
            writer_pos = cat.get_y_axis_writer(page)
            return cls(
                header=PageCut(**sliced, y0=head, y1=cat_pos).result,
                body=PageCut(**sliced, y0=writer_pos, y1=fn_start).result,
                category=cat.element,
                writer=cat.writer,
                **fields,
            )
