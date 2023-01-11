from typing import List

from django.db import transaction
from django.db.models import OuterRef, Exists, Subquery, Value
from django.shortcuts import get_object_or_404
from django.utils import timezone
from ninja import Router
from ninja.errors import HttpError
from ninja.pagination import paginate

from userbooks.helpers import check_unfinished_session
from userbooks.models import Shelf, UserBook, UserBookSession
from userbooks.schemas import (
    ShelfIn, ShelfOut, ShelfBookIn, UserBookIn, UserBookUpdate, UserBookOut,
    CurrentlyReadingIn, UserBookSessionOut, UserBookSessionIn, ReadingProgressIn, CurrentlyReadingBookOut, ShelfBookOut
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


@router.get("/books/read/all", response=List[UserBookOut])
@paginate
def list_read_books(request):
    all_book_finished_sessions = UserBookSession.objects.filter(
        userbook=OuterRef("pk"),
        finished_at__isnull=False
    )

    return (
        UserBook.objects
        .filter(created_by=request.user)
        .annotate(read=Exists(all_book_finished_sessions))
        .filter(read=True)
        .order_by("-updated_at")
    )


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

    session = check_unfinished_session(book_id)

    if session:
        raise HttpError(
            400,
            f"You have unfinished session {session.started_at.strftime('%d %b %Y %H:%M:%S')} for this book"
        )

    UserBookSession.objects.create(
        created_by=user,
        userbook=userbook,
        started_at=payload.started_at or timezone.now(),
        finished_at=payload.finished_at
    )

    return 201


@router.delete("/books/{book_id}/sessions/{session_id}")
def delete_user_book_session(request, book_id: int, session_id: int):
    user = request.user
    userbook = get_object_or_404(UserBook, pk=book_id, created_by=user)
    session = get_object_or_404(UserBookSession, pk=session_id, userbook=userbook)

    session.delete()

    return 200


@router.put("/books/{book_id}/done")
def mark_book_as_done(request, book_id: int):
    user = request.user
    userbook = get_object_or_404(UserBook, pk=book_id, created_by=user)

    session = check_unfinished_session(book_id)

    with transaction.atomic():
        if session:
            session.finished_at = timezone.now()
            session.save()

        if not session:
            UserBookSession.objects.create(
                created_by=user,
                userbook=userbook,
                started_at=timezone.now(),
                finished_at=timezone.now()
            )

        userbook.is_currently_reading = False
        userbook.progress = None
        userbook.progress_updated_at = None
        userbook.save()

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
def get_shelves(request, has_books: bool = False):
    if has_books:
        shelf_books = UserBook.objects.filter(
            created_by=request.user,
            shelves=OuterRef("pk")
        )
        return Shelf.objects.annotate(has_books=Exists(shelf_books)).filter(has_books=True)
        
    return Shelf.objects.filter(created_by=request.user)


@router.put("/shelves/{shelf_id}")
def update_shelf(request, shelf_id: int, payload: ShelfIn):
    shelf = get_object_or_404(Shelf, pk=shelf_id, created_by=request.user)
    shelf.name = payload.name
    shelf.save()
    return 200


@router.get("/shelves/{shelf_id}/books", response=List[ShelfBookOut])
@paginate
def get_shelf_books(request, shelf_id: int):
    shelf = get_object_or_404(Shelf, pk=shelf_id, created_by=request.user)
    return shelf.all_userbooks.annotate(shelf_name=Value(shelf.name)).all()


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


@router.get("/currently-reading", response=List[CurrentlyReadingBookOut])
@paginate
def get_currently_reading(request):
    all_book_unfinished_sessions = UserBookSession.objects.filter(
        userbook=OuterRef("pk"),
        finished_at__isnull=True
    )

    return (
        UserBook.objects
        .filter(created_by=request.user, is_currently_reading=True)
        .annotate(progress=Subquery(all_book_unfinished_sessions.values("progress")))
    )


@router.put("/currently-reading")
def update_currently_reading(request, payload: CurrentlyReadingIn):
    userbook = get_object_or_404(UserBook, id=payload.user_book_id, created_by=request.user)
    userbook.is_currently_reading = payload.status
    userbook.save()
    user = request.user

    session = check_unfinished_session(userbook.id)
    if not session:
        UserBookSession.objects.create(
            created_by=user,
            userbook=userbook,
            started_at=timezone.now()
        )

    return 200


@router.put("/currently-reading/progress")
def update_currently_reading_progress(request, payload: ReadingProgressIn):
    userbook = get_object_or_404(UserBook, id=payload.user_book_id, created_by=request.user)

    if not userbook.is_currently_reading:
        raise HttpError(400, "Book is not currently reading")

    if payload.progress > userbook.book.pages:
        raise HttpError(400, "Progress is greater than book pages")

    current_book_session = check_unfinished_session(userbook.id)

    if not current_book_session:
        UserBookSession.objects.create(
            created_by=request.user,
            userbook=userbook,
            progress=payload.progress,
            progress_updated_at=timezone.now(),
            started_at=timezone.now()
        )

    if current_book_session:
        current_book_session.progress = payload.progress
        current_book_session.progress_updated_at = timezone.now()
        current_book_session.save()

    return 200
