from dataclasses import KW_ONLY, dataclass, field
from datetime import datetime
from typing import Any, Type
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


@dataclass
class Chapter:
    _: KW_ONLY

    session: requests.Session = field(default_factory=requests.Session, repr=False)

    title: str | None = None
    summary: str | None = None
    notes: str | None = None
    article: str | None = None
    end_notes: str | None = None


class Descriptor:
    def __set_name__(self, owner: Type["Work"], name: str) -> None:
        self.name = f"_{name}"

    def __get__(self, instance: "Work", owner: Type["Work"]) -> Any:
        if instance is None:
            return self

        if not hasattr(instance, self.name):
            from ao3.tag import Tag

            resp = instance.session.get(
                urljoin("https://archiveofourown.org", instance.href)
            )

            soup = BeautifulSoup(resp.text, features="lxml")

            for dd in (
                soup.find("div", {"class": "wrapper"})
                .find("dl", {"class": "work meta group"})  # type: ignore
                .find_all("dd")  # type: ignore
            ):
                match dd["class"]:
                    case ["rating", "tags"]:
                        setattr(
                            instance,
                            "_rating",
                            [
                                Tag(
                                    session=instance.session,
                                    name=a.text,
                                    href=a["href"],
                                )
                                for a in dd.find("ul", {"class": "commas"}).find_all(
                                    "a", {"class": "tag"}
                                )
                            ],
                        )

                    case ["warning", "tags"]:
                        setattr(
                            instance,
                            "_archive_warning",
                            [
                                Tag(
                                    session=instance.session,
                                    name=a.text,
                                    href=a["href"],
                                )
                                for a in dd.find("ul", {"class": "commas"}).find_all(
                                    "a", {"class": "tag"}
                                )
                            ],
                        )

                    case ["category", "tags"]:
                        setattr(
                            instance,
                            "_category",
                            [
                                Tag(
                                    session=instance.session,
                                    name=a.text,
                                    href=a["href"],
                                )
                                for a in dd.find("ul", {"class": "commas"}).find_all(
                                    "a", {"class": "tag"}
                                )
                            ],
                        )

                    case ["fandom", "tags"]:
                        setattr(
                            instance,
                            "_fandom",
                            [
                                Tag(
                                    session=instance.session,
                                    name=a.text,
                                    href=a["href"],
                                )
                                for a in dd.find("ul", {"class": "commas"}).find_all(
                                    "a", {"class": "tag"}
                                )
                            ],
                        )

                    case ["relationship", "tags"]:
                        setattr(
                            instance,
                            "_relationships",
                            [
                                Tag(
                                    session=instance.session,
                                    name=a.text,
                                    href=a["href"],
                                )
                                for a in dd.find("ul", {"class": "commas"}).find_all(
                                    "a", {"class": "tag"}
                                )
                            ],
                        )

                    case ["language"]:
                        setattr(instance, "_language", dd.text.strip())

                    case ["stats"]:
                        stats = dd.find("dl", {"class": "stats"})

                        if elem := stats.find("dd", {"class": "published"}):
                            setattr(
                                instance,
                                "_published",
                                datetime.fromisoformat(elem.text),
                            )

                        if elem := stats.find("dd", {"class": "status"}):
                            setattr(
                                instance, "_status", datetime.fromisoformat(elem.text)
                            )
                            setattr(instance, "_complete", False)
                        else:
                            setattr(instance, "_status", None)
                            setattr(instance, "_complete", True)

                        if elem := stats.find("dd", {"class": "words"}):
                            setattr(instance, "_words", int(elem.text.replace(",", "")))

                        if elem := stats.find("dd", {"class": "chapters"}):
                            chapter, chapter_count = elem.text.split("/")

                            setattr(instance, "_chapter_number", int(chapter))
                            setattr(
                                instance,
                                "_chapter_count",
                                None if chapter_count == "?" else int(chapter_count),
                            )

                        if elem := stats.find("dd", {"class": "comments"}):
                            setattr(
                                instance, "_comments", int(elem.text.replace(",", ""))
                            )

                        if elem := stats.find("dd", {"class": "kudos"}):
                            setattr(instance, "_kudos", int(elem.text.replace(",", "")))

                        if elem := stats.find("dd", {"class": "hits"}):
                            setattr(instance, "_hits", int(elem.text.replace(",", "")))

            workskin = soup.find("div", {"id": "workskin"})

            preface = workskin.find("div", {"class": "preface group"})  # type: ignore

            setattr(
                instance,
                "_title",
                preface.find("h2", {"class": "title heading"}).text.strip(),  # type: ignore
            )

            if elem := preface.find("h3", {"class": "byline heading"}).find(  # type: ignore
                "a",
                {"rel": "author"},  # type: ignore
            ):
                setattr(instance, "_author", elem.text)  # type: ignore
            else:
                setattr(instance, "_author", None)

            if elem := preface.find("div", {"class": "summary module"}):  # type: ignore
                setattr(
                    instance,
                    "_summary",
                    "\n".join(
                        elem.find("blockquote", {"class": "userstuff"}).strings  # type: ignore
                    ).strip(),
                )

            chapters = []

            for chapter in workskin.find("div", {"id": "chapters"}).find_all(  # type: ignore
                "div", {"class": "chapter"}, recursive=False
            ):
                c = Chapter(session=instance.session)

                if elem := chapter.find("h3", {"class": "title"}):
                    setattr(c, "title", elem.text)

                if elem := chapter.find("div", {"id": "summary"}):
                    setattr(
                        c,
                        "summary",
                        "\n".join(
                            elem.find("blockquote", {"class": "userstuff"}).strings
                        ).strip(),
                    )

                if (elem := chapter.find("div", {"id": "notes"})) and (
                    notes := elem.find("blockquote", {"class": "userstuff"})
                ):
                    setattr(c, "notes", "\n".join(notes.strings).strip())

                if elem := chapter.find("div", {"role": "article"}):
                    setattr(c, "article", "\n".join(elem.strings).strip())

                if elem := chapter.find("div", {"class": "end notes module"}):
                    setattr(
                        c,
                        "end_notes",
                        "\n".join(
                            elem.find("blockquote", {"class": "userstuff"}).strings
                        ).strip(),
                    )

                chapters.append(c)

            if elem := workskin.find("div", {"class": "userstuff"}):  # type: ignore
                chapters.append(
                    Chapter(session=instance.session, article="\n".join(elem.strings))  # type: ignore
                )

            setattr(instance, "_chapters", chapters)

        if not hasattr(instance, self.name):
            setattr(instance, self.name, None)
            return

        return getattr(instance, self.name)

    def __set__(self, instance: "Work", value: Any) -> None:
        setattr(instance, f"_{value}", value)


@dataclass
class Work:
    _: KW_ONLY

    session: requests.Session = field(default_factory=requests.Session)

    href: str

    work_id: Descriptor = Descriptor()
    chapter_id: Descriptor = Descriptor()

    rating: Descriptor = Descriptor()
    archive_warning: Descriptor = Descriptor()
    fandoms: Descriptor = Descriptor()
    relationships: Descriptor = Descriptor()
    characters: Descriptor = Descriptor()
    additional_tags: Descriptor = Descriptor()
    language: Descriptor = Descriptor()

    published: Descriptor = Descriptor()
    status: Descriptor = Descriptor()
    words: Descriptor = Descriptor()
    chapter_number: Descriptor = Descriptor()
    chapter_count: Descriptor = Descriptor()
    comments: Descriptor = Descriptor()
    kudos: Descriptor = Descriptor()
    bookmarks: Descriptor = Descriptor()
    hits: Descriptor = Descriptor()

    author: Descriptor = Descriptor()
    title: Descriptor = Descriptor()
    summary: Descriptor = Descriptor()

    chapters: Descriptor = Descriptor()

    def __post_init__(self) -> None:
        match [part for part in urlparse(self.href).path.split("/") if part]:
            case ["works", work_id, "chapters", chapter_id]:
                setattr(self, "_work_id", int(work_id))
                setattr(self, "_chapter_id", int(chapter_id))

            case ["works", work_id]:
                setattr(self, "_work_id", int(work_id))
                setattr(self, "_chapter_id", None)

            case _:
                raise ValueError(f"Unknow href: {self.href}")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.title}, author={self.author})"
