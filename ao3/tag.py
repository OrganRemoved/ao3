import re
from dataclasses import KW_ONLY, dataclass, field
from itertools import groupby
from operator import itemgetter
from typing import Any, Type
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


class Descriptor:
    def __set_name__(self, owner: Type["Tag"], name: str) -> None:
        self.name = f"_{name}"

    def __get__(self, instance: "Tag", owner: Type["Tag"]) -> Any:
        if instance is None:
            return self

        if not hasattr(instance, self.name):
            from ao3.work import Work

            resp = instance.session.get(
                urljoin("https://archiveofourown.org", instance.href),
                params={"page": instance.page, "view_adult": instance.view_adult},
            )

            soup = BeautifulSoup(resp.text, features="lxml")

            if urlparse(resp.url).path.endswith("/works"):
                if works_count := re.search(
                    r"(?P<works_count>[0-9,]+) Works",
                    soup.find("h2", {"class": "heading"}).text,  # type: ignore
                ):
                    setattr(
                        instance,
                        "_works_count",
                        int(works_count.groupdict()["works_count"].replace(",", "")),
                    )

                works = []

                for li in soup.find("ol", {"class": "work index group"}).find_all(  # type: ignore
                    "li", {"role": "article"}
                ):
                    header = li.find("div", {"class": "header module"})

                    title = header.find("h4", {"class": "heading"}).find("a")

                    work = Work(session=instance.session, href=title["href"])

                    setattr(work, "_title", title.text)

                    if elem := header.find("h4", {"class": "heading"}).find(
                        "a", {"rel": "author"}
                    ):
                        setattr(work, "_author", elem.text)

                    rating, warnings, category, complete = header.find(
                        "ul", {"class": "required-tags"}
                    ).find_all("li")

                    setattr(
                        work,
                        "_complete",
                        bool(complete.find("span", {"class": "complete-yes"})),
                    )

                    for class_, grouper in groupby(
                        li.find("ul", {"class": "tags commas"}).find_all("li"),
                        key=itemgetter("class"),
                    ):
                        match class_:
                            case ["warnings"]:
                                setattr(
                                    work,
                                    "_archive_warning",
                                    [
                                        Tag(
                                            session=instance.session,
                                            name=a.text,
                                            href=a["href"],
                                        )
                                        for tag in grouper
                                        if (a := tag.find("a", {"class": "tag"}))
                                    ],
                                )

                            case ["relationships"]:
                                setattr(
                                    work,
                                    "_relationships",
                                    [
                                        Tag(
                                            session=instance.session,
                                            name=a.text,
                                            href=a["href"],
                                        )
                                        for tag in grouper
                                        if (a := tag.find("a", {"class": "tag"}))
                                    ],
                                )

                            case ["characters"]:
                                setattr(
                                    work,
                                    "_characters",
                                    [
                                        Tag(
                                            session=instance.session,
                                            name=a.text,
                                            href=a["href"],
                                        )
                                        for tag in grouper
                                        if (a := tag.find("a", {"class": "tag"}))
                                    ],
                                )

                            case ["freeforms"]:
                                setattr(
                                    work,
                                    "_additional_tags",
                                    [
                                        Tag(
                                            session=instance.session,
                                            name=a.text,
                                            href=a["href"],
                                        )
                                        for tag in grouper
                                        if (a := tag.find("a", {"class": "tag"}))
                                    ],
                                )

                    stats = li.find("dl", {"class": "stats"})

                    if elem := stats.find("dd", {"class": "language"}):
                        setattr(work, "_language", elem.text)

                    if elem := stats.find("dd", {"class": "words"}):
                        setattr(work, "_words", int(elem.text.replace(",", "")))

                    if elem := stats.find("dd", {"class": "chapters"}):
                        chapter, chapter_count = elem.text.split("/")

                        setattr(work, "_chapter_number", int(chapter))
                        setattr(
                            work,
                            "_chapter_count",
                            None if chapter_count == "?" else int(chapter_count),
                        )

                    if elem := stats.find("dd", {"class": "comments"}):
                        setattr(work, "_comments", int(elem.text))

                    if elem := stats.find("dd", {"class": "kudos"}):
                        setattr(work, "_kudos", int(elem.text))

                    if elem := stats.find("dd", {"class": "hits"}):
                        setattr(work, "_hits", int(elem.text.replace(",", "")))

                    if elem := li.find("blockquote", {"class": "userstuff summary"}):
                        setattr(work, "_summary", "\n".join(elem.strings).strip())

                    works.append(work)

                setattr(instance, "_works", works)

            else:
                raise NotImplementedError

        if not hasattr(instance, self.name):
            setattr(instance, self.name, None)
            return

        return getattr(instance, self.name)

    def __set__(self, instance: "Tag", value: Any) -> None:
        setattr(instance, f"_{value}", value)


@dataclass
class Tag:
    _: KW_ONLY

    session: requests.Session = field(default_factory=requests.Session)

    name: str
    href: str

    view_adult: bool = True

    letter: str | None = None

    works: Descriptor = Descriptor()
    works_count: Descriptor = Descriptor()
    bookmarks: Descriptor = Descriptor()
    page: int = 1
    page_count: Descriptor = Descriptor()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name})"
