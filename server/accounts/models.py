from django.contrib.auth import get_user_model
from django.db import models


def user_directory_path(instance, filename):
    return f'images/users/{instance.user.id}/profile/{filename}'


class Profile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    image = models.ImageField(upload_to=user_directory_path, blank=True)

    def __str__(self):
        return self.user.username