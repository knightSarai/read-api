from typing import List

from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db import transaction
from django.db.models import Exists, OuterRef, Subquery
from django.shortcuts import get_object_or_404
from books.helper import annotate_user_book_id
from ninja import Router, Query, File
from ninja.errors import HttpError
from ninja.files import UploadedFile
from ninja.pagination import paginate

from books.models import Book, Genre
from books.schemas import BookIn, BookQueryParams, BookOut, BookSearch, GenreIn, GenreOut
from userbooks.models import UserBook

router = Router()


@router.get("/search", response=List[BookSearch], auth=None)
@paginate
def search_books(request, query: BookQueryParams = Query(...), exclude_library: bool = False):
    query = query.dict(exclude_unset=True)

    search_vector = None
    query_string = ''
    for k, v in query.items():
        query_string += ' ' + v
        if search_vector is None:
            search_vector = SearchVector(k, weight='A' if k == 'title' else 'B')
        else:
            search_vector += SearchVector(k, weight='A' if k == 'title' else 'B')

    search_query = SearchQuery(query_string)

    books = (
        Book.objects
        .annotate(
            search=search_vector,
            rank=SearchRank(search_vector, search_query),
        )
        .filter(rank__gte=0.2)
        .order_by("-rank")
    )

    user = request.user
    if user.is_authenticated:
        books = annotate_user_book_id(books, user)

        if exclude_library:
            books = books.filter(user_book_id__isnull=True)

    return books


@router.post("/genres")
def create_genre(request, payload: GenreIn):
    genre = Genre.objects.create(
        created_by=request.user,
        name=payload.name
    )

    return {"id": genre.id}


@router.get("/genres", response=List[GenreOut], auth=None)
def get_genres(request):
    return Genre.objects.all()


@router.post("")
def create_book(request, payload: BookIn):
    genres = payload.dict(include={"genres"}).get("genres")

    with transaction.atomic():
        book = Book.objects.create(
            created_by=request.user,
            **payload.dict(exclude_unset=True, exclude={"genres"}),
        )

        if genres:
            book.genres.set(Genre.objects.filter(pk__in=genres))

    return {"id": book.id}


@router.get("", response=List[BookOut], auth=None)
@paginate
def get_books(request):
    return Book.objects.all()


@router.put("/{book_id}")
def update_book(request, book_id: int, payload: BookIn):
    genres = payload.dict(include={"genres"})["genres"]

    with transaction.atomic():
        book = get_object_or_404(Book, pk=book_id)

        for k, v in payload.dict(exclude_unset=True, exclude={"genres"}).items():
            setattr(book, k, v)
        book.save()

        if genres is not None:
            book.genres.clear()
            book.genres.set(Genre.objects.filter(pk__in=genres))

    return {"id": book.id}


@router.post("/{book_id}/image")
def upload_book_image(request, book_id: int, image: UploadedFile = File(...)):
    book = get_object_or_404(Book, pk=book_id)
    book.image.delete()
    book.image = image
    book.save()

    return {"id": book.id}


@router.delete("/{book_id}/image")
def delete_book_image(request, book_id: int):
    book = get_object_or_404(Book, pk=book_id)
    book.image.delete()

    return 204


@router.get("/{book_id}", response=BookOut, auth=None)
def get_book_by_id(request, book_id: int):
    try:
        book = Book.objects.filter(pk=book_id)

        if not book.exists():
            raise Book.DoesNotExist

        if book.count() > 1:
            raise Book.MultipleObjectsReturned

        user = request.user
        if user.is_authenticated:
            book = annotate_user_book_id(book, user)


    except Book.DoesNotExist:
        raise HttpError(404, "Book not found")
    except Book.MultipleObjectsReturned:
        raise HttpError(500, "Multiple books found")

    return book.first()


@router.get("/{book_id}/genres", response=List[GenreOut], auth=None)
def get_genres_by_book_id(request, book_id: int):
    book = get_object_or_404(Book, id=book_id)
    genres = book.genres.all()
    return genres
