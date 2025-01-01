from dataclasses import KW_ONLY, dataclass
from typing import List

import requests

from ao3.tag import Tag

@dataclass
class Fandom:
    _: KW_ONLY

    session: requests.Session

    name: str
    href: str | None = None

    hot_tags: List[Tag] | None = None
    tags: List[Tag] | None = None
