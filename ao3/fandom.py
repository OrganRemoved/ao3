import re
from dataclasses import KW_ONLY, dataclass, field
from functools import cached_property
from typing import List
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from ao3.tag import Tag


@dataclass
class Fandom:
    _: KW_ONLY

    session: requests.Session = field(default_factory=requests.Session)

    name: str

    def __post_init__(self) -> None:
        soup = BeautifulSoup(
            self.session.get("https://archiveofourown.org/media").text, features="lxml"
        )

        for li in soup.find("ul", {"class": "media fandom index group"}).find_all(  # type: ignore
            "li", {"class": "medium listbox group"}
        ):
            if heading := li.find("h3", {"class": "heading"}).find(
                "a", string=self.name
            ):
                self.href = heading["href"]

                self.hot_tags = [
                    Tag(
                        session=self.session,
                        name=a.text,
                        href=a["href"],
                        works_count=int(
                            re.search(
                                r"\((?P<works_count>\d+)\)", fandom.text
                            ).groupdict()["works_count"]  # type: ignore
                        ),
                    )
                    for fandom in li.find("ol", {"class": "index group"}).find_all("li")
                    if (a := fandom.find("a", {"class": "tag"}))
                ]

    @cached_property
    def tags(self) -> List[Tag]:
        soup = BeautifulSoup(
            self.session.get(urljoin("https://archiveofourown.org", self.href)).text,
            features="lxml",
        )

        return [
            Tag(
                session=self.session,
                name=a.text,
                href=a["href"],
                letter=li["id"].split("-")[1],
            )
            for li in soup.find(
                "ol", {"class": "alphabet fandom index group"}
            ).find_all("li", {"class": "letter listbox group"})  # type: ignore
            for li_ in li.find("ul", {"class": "tags index group"}).find_all("li")
            if (a := li_.find("a", {"class": "tag"}))
        ]

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name})"
