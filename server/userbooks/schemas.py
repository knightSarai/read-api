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


class UserBookIn(Schema):
    book_id: int
    shelves: Optional[List[int]]


class UserBookUpdate(Schema):
    shelves: Optional[List[int]]


class UserBookOut(Schema):
    id: int
    book: BookOut
