from rest_framework.test import APITestCase
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError
from apps.movie.models import Movie
from apps.room.models import Room
from apps.session.models import Session
from apps.seat.models import Seat


class SessionModelTests(APITestCase):

    def setUp(self):
        self.movie = Movie.objects.create(
            name="Stalker",
            duration=163,
            genre="Sci-Fi/Drama",
            director="Andrei Tarkovsky",
            description="Um guia leva duas pessoas através de uma área perigosa conhecida como A Zona."
        )
        self.room = Room.objects.create(
            name="Sala Tarkovsky",
            rows=10,
            seats_per_row=10
        )
        self.start_time = timezone.now() + timedelta(days=1)

    def test_session_auto_calculates_end_time(self):
        session = Session.objects.create(
            movie=self.movie,
            room=self.room,
            starts_at=self.start_time
        )
        expected_end = self.start_time + timedelta(minutes=self.movie.duration)
        self.assertEqual(session.ends_at, expected_end)

    def test_session_creates_seats_automatically(self):
        session = Session.objects.create(
            movie=self.movie,
            room=self.room,
            starts_at=self.start_time
        )
        expected_seats = self.room.rows * self.room.seats_per_row
        self.assertEqual(Seat.objects.filter(session=session).count(), expected_seats)

        first_seat = Seat.objects.filter(session=session, row='A', number=1).first()
        self.assertIsNotNone(first_seat)

    def test_prevent_overlapping_sessions_in_same_room(self):
        Session.objects.create(
            movie=self.movie,
            room=self.room,
            starts_at=self.start_time
        )

        overlap_session = Session(
            movie=self.movie,
            room=self.room,
            starts_at=self.start_time + timedelta(minutes=60)
        )

        with self.assertRaises(ValidationError):
            overlap_session.save()

    def test_allow_sessions_in_different_rooms_at_same_time(self):
        room_solaris = Room.objects.create(name="Sala Solaris", rows=5, seats_per_row=5)

        Session.objects.create(
            movie=self.movie,
            room=self.room,
            starts_at=self.start_time
        )

        session2 = Session(
            movie=self.movie,
            room=room_solaris,
            starts_at=self.start_time
        )

        try:
            session2.save()
        except ValidationError:
            self.fail("ValidationError raised unexpectedly")

    def test_manager_get_by_movie(self):
        session = Session.objects.create(
            movie=self.movie,
            room=self.room,
            starts_at=self.start_time
        )
        sessions = Session.objects.get_by_movie(self.movie.id)
        self.assertIn(session, sessions)