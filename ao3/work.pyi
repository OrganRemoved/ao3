from dataclasses import KW_ONLY, dataclass
from datetime import datetime
from typing import List

import requests

from ao3.tag import Tag

@dataclass
class Chapter:
    _: KW_ONLY

    session: requests.Session

    title: str | None = None
    summary: str | None = None
    notes: str | None = None
    article: str | None = None
    end_notes: str | None = None

@dataclass
class Work:
    _: KW_ONLY

    session: requests.Session

    href: str | None = None

    work_id: int | None = None
    chapter_id: int | None = None

    rating: List[Tag] | None = None
    archive_warning: List[Tag] | None = None
    fandoms: List[Tag] | None = None
    relationships: List[Tag] | None = None
    characters: List[Tag] | None = None
    additional_tags: List[Tag] | None = None
    language: str | None = None

    complete: bool | None = None

    published: datetime | None = None
    status: datetime | None = None
    words: int | None = None
    chapter_number: int | None = None
    chapter_count: int | None = None
    comments: int | None = None
    kudos: int | None = None
    bookmarks: int | None = None
    hits: int | None = None

    author: str | None = None
    title: str | None = None
    summary: str | None = None

    chapters: List[Chapter] | None = None
