from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from base.models import BaseModel


class Vote(BaseModel):
    review = models.ForeignKey('reviews.Review', on_delete=models.CASCADE)
    up = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['review', 'created_by']


class Review(BaseModel):
    userbook = models.OneToOneField('userbooks.UserBook', on_delete=models.CASCADE)
    rating = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    body = models.TextField()
    votes = models.ManyToManyField(get_user_model(), through=Vote, related_name='votes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)
    is_private = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.created_by} - {self.userbook} - Review'

