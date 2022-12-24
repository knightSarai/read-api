from django.db import models


class BookManager(models.Manager):
    def create_with_user(self, data):
        book = self.model()

        for key, value in data.items():
            setattr(book, key, value)
        book.save()

        return book
