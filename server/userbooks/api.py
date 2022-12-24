from typing import List

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from ninja import Router
from ninja.errors import HttpError
from ninja.pagination import paginate

from userbooks.exceptions import UserBookSessionAlreadyExists
from userbooks.helpers import check_unfinished_session
from userbooks.models import Shelf, UserBook, UserBookSession
from userbooks.schemas import (
    ShelfIn, ShelfOut, ShelfBookIn, UserBookIn, UserBookUpdate, UserBookOut,
    CurrentlyReadingIn, UserBookSessionOut, UserBookSessionIn
)

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


@router.get("/books", response=List[UserBookOut])
@paginate
def list_user_books(request):
    return UserBook.objects.filter(created_by=request.user)


@router.put("/books/{book_id}")
def update_user_books(request, book_id: int, payload: UserBookUpdate):
    shelves = payload.dict().get('shelves')
    user_book = get_object_or_404(UserBook, pk=book_id, created_by=request.user)
    user_book.shelves.clear()
    user_book.shelves.set(Shelf.objects.filter(pk__in=shelves))

    return 200


@router.delete("/books/{book_id}")
def delete_user_books(request, book_id: int):
    user_book = get_object_or_404(UserBook, pk=book_id, created_by=request.user)
    user_book.delete()

    return 200


@router.get("/books/{book_id}/sessions", response=List[UserBookSessionOut])
def list_user_book_sessions(request, book_id: int):
    return UserBookSession.objects.filter(created_by=request.user, userbook__pk=book_id)


@router.post("/books/{book_id}/sessions")
def create_user_book_session(request, book_id: int, payload: UserBookSessionIn):
    user = request.user
    userbook = get_object_or_404(UserBook, pk=book_id, created_by=user)

    try:
        check_unfinished_session(book_id)

        UserBookSession.objects.create(
            created_by=user,
            userbook=userbook,
            started_at=payload.started_at or timezone.now(),
            finished_at=payload.finished_at
        )

        userbook.is_currently_reading = not payload.finished_at
        userbook.save()

    except UserBookSessionAlreadyExists as e:
        raise HttpError(400, str(e))

    return 201


@router.put("/books/{book_id}/sessions/{session_id}")
def update_user_book_session(request, book_id: int, session_id: int, payload: UserBookSessionIn):
    user_book_session = get_object_or_404(
        UserBookSession,
        pk=session_id,
        userbook__pk=book_id,
        created_by=request.user
    )

    user_book_session.started_at = payload.started_at or user_book_session.started_at
    user_book_session.finished_at = payload.finished_at or user_book_session.finished_at
    user_book_session.save()

    return 200


@router.post("/shelves")
def create_shelf(request, payload: ShelfIn):
    shelf = Shelf.objects.create(created_by=request.user, **payload.dict())
    return {"id": shelf.id}


@router.get("/shelves", response=List[ShelfOut])
def get_shelves(request):
    return Shelf.objects.filter(created_by=request.user)


@router.put("/shelves/{shelf_id}")
def update_shelf(request, shelf_id: int, payload: ShelfIn):
    shelf = get_object_or_404(Shelf, pk=shelf_id, created_by=request.user)
    shelf.name = payload.name
    shelf.save()
    return 200


@router.get("/shelves/{shelf_id}/books", response=List[UserBookOut])
@paginate
def get_shelf_books(request, shelf_id: int):
    shelf = get_object_or_404(Shelf, pk=shelf_id, created_by=request.user)
    return shelf.all_userbooks.all()


@router.post("/shelves/{shelf_id}/books")
def add_book_to_shelf(request, shelf_id: int, payload: ShelfBookIn):
    shelf = get_object_or_404(Shelf, pk=shelf_id, created_by=request.user)
    book = get_object_or_404(UserBook, id=payload.user_book_id, created_by=request.user)
    book.shelves.add(shelf)

    return 201


@router.delete("/shelves/{shelf_id}/books/{user_book_id}")
def remove_book_from_shelf(request, shelf_id: int, user_book_id: int):
    shelf = get_object_or_404(Shelf, pk=shelf_id, created_by=request.user)
    user_book = get_object_or_404(UserBook, id=user_book_id, created_by=request.user)
    user_book.shelves.remove(shelf)
    return 204


@router.get("/currently-reading", response=List[UserBookOut])
@paginate
def get_currently_reading(request):
    return UserBook.objects.filter(created_by=request.user, is_currently_reading=True)


@router.put("/currently-reading")
def update_currently_reading(request, payload: CurrentlyReadingIn):
    userbook = get_object_or_404(UserBook, id=payload.user_book_id, created_by=request.user)
    userbook.is_currently_reading = payload.status
    userbook.save()
    finished_at = timezone.now() if not payload.status else None
    user = request.user

    try:
        if payload.status:
            check_unfinished_session(userbook.id)
            UserBookSession.objects.create(
                created_by=user,
                userbook=userbook,
                started_at=timezone.now()
            )
        else:
            (
                UserBookSession.objects
                .filter(
                    created_by=user,
                    userbook__pk=userbook.id,
                    finished_at=None
                )
                .update(finished_at=finished_at)
            )

    except UserBookSessionAlreadyExists:
        return 200

    return 200
