from userbooks.models import UserBook
from django.db.models import OuterRef, Subquery

def annotate_user_book_id(books, user):
    user_book = UserBook.objects.filter(
        book=OuterRef('pk'),
        created_by=user
    ).values('pk')

    books = books.annotate(
        user_book_id=Subquery(user_book)
    )

    return books
