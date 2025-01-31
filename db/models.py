from typing import Any, Callable

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

from settings import AUTH_USER_MODEL


class Genre(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        return self.name


class Actor(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Movie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    actors = models.ManyToManyField(Actor, related_name="movies")
    genres = models.ManyToManyField(Genre, related_name="movies")

    class Meta:
        indexes = [models.Index(fields=["title"])]

    def __str__(self) -> str:
        return self.title


class CinemaHall(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row

    def __str__(self) -> str:
        return self.name


class MovieSession(models.Model):
    show_time = models.DateTimeField()
    cinema_hall = models.ForeignKey(CinemaHall,
                                    on_delete=models.CASCADE,
                                    related_name="movie_sessions")
    movie = models.ForeignKey(Movie,
                              on_delete=models.CASCADE,
                              related_name="movie_sessions")

    def __str__(self) -> str:
        return f"{self.movie.title} {str(self.show_time)}"


class User(AbstractUser):
    pass


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name="orders")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.created_at}"


class Ticket(models.Model):
    movie_session = models.ForeignKey(MovieSession,
                                      on_delete=models.CASCADE,
                                      related_name="tickets")
    order = models.ForeignKey(Order,
                              on_delete=models.CASCADE,
                              related_name="orders")
    row = models.IntegerField()
    seat = models.IntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["row", "seat", "movie_session"],
                                    name="no ticket duplicates")
        ]

    def __str__(self) -> str:
        return (f"{self.movie_session.movie.title} "
                f"{self.movie_session.show_time} "
                f"(row: {self.row}, seat: {self.seat})")

    def clean(self) -> None:
        rows = self.movie_session.cinema_hall.rows
        seats = self.movie_session.cinema_hall.seats_in_row
        if not 1 <= self.row <= rows:
            raise ValidationError({"row": "row number must be in "
                                          "available range: "
                                          f"(1, rows): (1, {rows})"})
        if not 1 <= self.seat <= seats:
            raise ValidationError({"seat": "seat number must be in "
                                           "available range: "
                                           f"(1, seats_in_row): (1, {seats})"})

    def save(self,
             force_insert: bool = False,
             force_update: bool = False,
             using: Any = None,
             update_fields: Any = None) -> Callable:
        self.full_clean()
        return super().save(force_insert, force_update, using, update_fields)
