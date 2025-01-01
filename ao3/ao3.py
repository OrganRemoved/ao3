import logging
from typing import Literal

import requests

from ao3.fandom import Fandom
from ao3.tag import Tag
from ao3.work import Work

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s][%(levelname)s][%(module)s:%(funcName)s:%(lineno)d]: %(message)s",
)


class AO3:
    def __init__(self) -> None:
        self.session = requests.Session()

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
    ) -> Fandom:
        return Fandom(session=self.session, name=fandom)

    def get_tag(self, tag: str, page: int = 1, view_adult: bool = True) -> Tag:
        return Tag(
            session=self.session,
            name=tag,
            href=f"/tags/{tag}/works",
            page=page,
            view_adult=view_adult,
        )

    def get_work(self, work_id: int, chapter_id: int | None = None) -> Work:
        return (
            Work(session=self.session, href=f"/works/{work_id}/chapters/{chapter_id}")
            if chapter_id
            else Work(session=self.session, href=f"/works/{work_id}")
        )
