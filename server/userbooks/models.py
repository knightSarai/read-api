from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.text import slugify

from base.models import BaseModel


class Shelf(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)

    def __str__(self):
        return f'{self.created_by} - {self.name}'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class UserBook(BaseModel):
    book = models.ForeignKey('books.Book', on_delete=models.CASCADE, related_name='all_userbooks')
    shelves = models.ManyToManyField('userbooks.Shelf', blank=True, related_name='all_userbooks')

    is_currently_reading = models.BooleanField(default=False)
    is_private = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.created_by} - {self.book}'


class UserBookSession(BaseModel):
    userbook = models.ForeignKey('userbooks.UserBook', on_delete=models.CASCADE, related_name='all_sessions')
    progress = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0)]
    )
    progress_updated_at = models.DateTimeField(blank=True, null=True)
    started_at = models.DateTimeField()
    finished_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f'{self.created_by} - {self.userbook} - {self.started_at}'
