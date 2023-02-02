import httpx
from sqlite_utils import Database
from pathlib import Path
from sqlite_utils.db import NotFoundError

SC_BASE_URL = "https://sc.judiciary.gov.ph"

def get_sc_pdf_from_id(dbpath: Path, id: int) -> Path:
    db = Database(dbpath)
    try:
        record = db['db_tbl_sc_web_decisions'].get(28688) # type: ignore
    except NotFoundError:
        raise Exception(f"Bad {id=}")
    res = httpx.get(f"{SC_BASE_URL}{record['pdf']}")
    target_file = Path().cwd() / "temp" / "temp.pdf"
    target_file.write_bytes(res.content)
    return target_file

