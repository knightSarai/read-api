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
    book = models.OneToOneField('books.Book', on_delete=models.CASCADE)
    shelves = models.ManyToManyField('userbooks.Shelf', blank=True, related_name='all_userbooks')
    rating = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    review = models.ForeignKey(
        'reviews.Review',
        related_name='all_userbooks',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    progress = models.IntegerField(blank=True, null=True)
    progress_updated_at = models.DateTimeField(blank=True, null=True)
    started_at = models.DateTimeField(blank=True, null=True)
    finished_at = models.DateTimeField(blank=True, null=True)
    is_private = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.created_by} - {self.book}'
