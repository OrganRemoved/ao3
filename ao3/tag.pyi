from dataclasses import KW_ONLY, dataclass
from typing import List

import requests

from ao3.work import Work

@dataclass
class Tag:
    _: KW_ONLY

    session: requests.Session

    name: str
    href: str

    view_adult: bool = True

    letter: str | None = None

    works: List[Work] | None = None
    works_count: int | None = None
    bookmarks: int | None = None
    page: int | None = None
    page_count: int | None = None
