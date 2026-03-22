from django.db import models

from apps.core.models import AbstractModel
from apps.movie.managers.movie_manager import MovieManager


class Movie(AbstractModel):
    name = models.CharField(max_length=100)
    duration = models.IntegerField()
    genre = models.CharField(max_length=100)
    director = models.CharField(max_length=100)
    description = models.TextField()

    objects = MovieManager()