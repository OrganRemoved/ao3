from typing import Literal

from ao3.fandom import Fandom
from ao3.tag import Tag
from ao3.work import Work

class AO3:
    def __init__(self) -> None: ...
    def get_fandom(
        self,
        fandom: Literal[
            "Anime & Manga",
            "Books & Literature",
            "Cartoons & Comics & Graphic Novels",
            "Celebrities & Real People",
            "Movies",
            "Music & Bands",
            "Other Media",
            "Theater",
            "TV Shows",
            "Video Games",
            "Uncategorized Fandoms",
        ],
    ) -> Fandom: ...
    def get_tag(self, tag: str, page: int = 1, view_adult: bool = True) -> Tag: ...
    def get_work(
        self, work_id: int, chapter_id: int | None = None, entire_work: bool = False
    ) -> Work: ...
