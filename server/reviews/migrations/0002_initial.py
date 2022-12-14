# Generated by Django 4.1.4 on 2022-12-23 21:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('userbooks', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('reviews', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='for_book',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='all_reviews', to='userbooks.userbook'),
        ),
        migrations.AddField(
            model_name='review',
            name='votes',
            field=models.ManyToManyField(related_name='votes', through='reviews.Vote', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='vote',
            unique_together={('review', 'created_by')},
        ),
    ]
