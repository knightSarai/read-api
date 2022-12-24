from typing import List

from django.db import transaction
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.pagination import paginate

from books.models import Book
from books.schemas import BookOut
from userbooks.models import Shelf, UserBook
from userbooks.schemas import ShelfIn, ShelfOut, ShelfBookIn, UserBookIn, UserBookUpdate, UserBookOut

router = Router()


@router.post("/books")
def create_user_books(request, payload: UserBookIn):
    shelves = payload.dict(include={"shelves"}).get("shelves")
    with transaction.atomic():
        user_book = UserBook.objects.create(
            created_by=request.user,
            **payload.dict(exclude={"shelves"})
        )

        if shelves:
            user_book.shelves.set(Shelf.objects.filter(pk__in=shelves))

    return 201


@router.put("/books/{book_id}")
def update_user_books(request, book_id: int, payload: UserBookUpdate):
    shelves = payload.dict().get('shelves')
    user_book = get_object_or_404(UserBook, pk=book_id, created_by=request.user)
    user_book.shelves.clear()
    user_book.shelves.set(Shelf.objects.filter(pk__in=shelves))

    return 200


@router.get("/books", response=List[UserBookOut])
@paginate
def list_user_books(request):
    return UserBook.objects.filter(created_by=request.user)


@router.post("/shelves")
def create_shelf(request, payload: ShelfIn):
    shelf = Shelf.objects.create(created_by=request.user, **payload.dict())
    return {"id": shelf.id}


@router.get("/shelves", response=List[ShelfOut])
def get_shelves(request):
    return Shelf.objects.filter(created_by=request.user)


@router.get("/shelves/{slug}/books", response=List[BookOut])
@paginate
def get_shelf_books(request, slug: str):
    shelf = get_object_or_404(Shelf, slug=slug, created_by=request.user)
    return shelf.all_userbooks.all()


@router.get("/shelves/{slug}/books")
def add_book_to_shelf(request, slug: str, payload: ShelfBookIn):
    shelf = get_object_or_404(Shelf, slug=slug, created_by=request.user)
    book = get_object_or_404(UserBook, id=payload.user_book_id, created_by=request.user)
    book.shelf = shelf
    book.save()
    return 201


@router.delete("/shelves/{slug}/books/{user_book_id}")
def remove_book_from_shelf(request, slug: str, user_book_id: int):
    shelf = get_object_or_404(Shelf, slug=slug, created_by=request.user)
    book = get_object_or_404(UserBook, id=user_book_id, created_by=request.user)
    book.shelf = None
    book.save()
    return 204
