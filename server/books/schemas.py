from datetime import date
from typing import Optional

from ninja import Schema
from pydantic import root_validator


class BookBase(Schema):
    title: str
    authors: str
    isbn: Optional[str]
    isbn13: Optional[str]
    language: str
    pages: int
    publication_date: Optional[date]
    publisher: Optional[str]
    description: Optional[str]


class BookIn(BookBase):
    genres: Optional[list[int]]


class BookOut(BookBase):
    id: int
    image: Optional[str]
    user_book_id: Optional[int]


class BookSearch(BookOut):
    user_book_id: Optional[int]


class BookQueryParams(Schema):
    title: Optional[str]
    authors: Optional[str]

    @root_validator(pre=True)
    def check_if_all_none(cls, values):
        if not any(values.values()):
            raise ValueError("At least one field must be provided")
        return values


class GenreIn(Schema):
    name: str


class GenreOut(GenreIn):
    id: int
