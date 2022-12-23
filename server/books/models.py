from django.db import models

from base.models import BaseModel


class Book(BaseModel):
    title = models.CharField(max_length=255)
    authors = models.CharField(max_length=255)
    rating = models.FloatField(blank=True, null=True)
    isbn = models.CharField(max_length=255, unique=True, null=True)
    isbn13 = models.CharField(max_length=255, unique=True, null=True)
    language = models.CharField(max_length=255, blank=True)
    pages = models.IntegerField()
    publication_date = models.DateField(max_length=255, null=True)
    publisher = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='images/%Y/%m/%d', blank=True)
    genres = models.ManyToManyField('Genre', related_name='books', blank=True)

    def __str__(self):
        return self.title


class Genre(BaseModel):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name
