from typing import List

from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.shortcuts import get_object_or_404
from ninja import Router, Query
from ninja.pagination import paginate

from books.models import Book, Genre
from books.schemas import BookIn, BookQueryParams, BookOut, GenreIn, GenreOut

router = Router()


@router.post("/")
def create_book(request, payload: BookIn):
    book = Book.objects.create(
        created_by=request.user,
        **payload.dict(exclude_unset=True)
    )

    return {"id": book.id}


@router.get("/search", response=List[BookOut], auth=None)
@paginate
def search_books(request, query: BookQueryParams = Query(...)):
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
            rank=SearchRank(search_vector, search_query)
        )
        .filter(rank__gte=0.2)
        .order_by("-rank")
    )

    return books


@router.get("/{user_id}", response=BookOut, auth=None)
def get_book_by_id(request, user_id: int):
    return get_object_or_404(Book, id=user_id)


@router.post("/genres/")
def create_genre(request, payload: GenreIn):
    genre = Genre.objects.create(
        created_by=request.user,
        name=payload.name
    )

    return {"id": genre.id}


@router.get("/genres/", response=List[GenreOut], auth=None)
def get_genres(request):
    return Genre.objects.all()
