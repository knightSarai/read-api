from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from ninja import Schema

from books.schemas import BookOut


class ShelfIn(Schema):
    name: str


class ShelfOut(ShelfIn):
    id: int
    slug: str


class ShelfBooksOut(ShelfOut):
    pass


class ShelfBookIn(Schema):
    user_book_id: int


class CurrentlyReadingIn(Schema):
    user_book_id: int
    status: bool


class UserBookIn(Schema):
    book_id: int
    shelves: Optional[List[int]]


class UserBookUpdate(Schema):
    shelves: Optional[List[int]]


class UserBookOut(Schema):
    id: int
    book: BookOut
    is_currently_reading: bool


class UserBookSessionBase(Schema):
    progress: Optional[Decimal]
    started_at: Optional[datetime]
    finished_at: Optional[datetime]


class UserBookSessionOut(UserBookSessionBase):
    id: int
    progress_updated_at: Optional[datetime]


class UserBookSessionIn(UserBookSessionBase):
    pass
