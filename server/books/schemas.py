from typing import Optional

from ninja import Schema
from pydantic import root_validator


class BookIn(Schema):
    title: str
    authors: str
    isbn: Optional[str]
    isbn13: Optional[str]
    language: str
    pages: int
    publication_date: Optional[str]
    publisher: Optional[str]
    description: Optional[str]
    genres: Optional[list[int]]


class BookOut(BookIn):
    id: int


class BookQueryParams(Schema):
    title: Optional[str]
    authors: Optional[str]

    @root_validator(pre=True)
    def check_if_all_none(cls, values):
        if not any(values.values()):
            raise ValueError("At least one field must be provided")
        return values

