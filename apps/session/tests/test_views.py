from rest_framework.test import APITestCase
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.core.cache import cache
from apps.movie.models import Movie
from apps.room.models import Room
from apps.session.models import Session
from apps.seat.models import Seat, OrderStatus

User = get_user_model()


class SessionViewSetTests(APITestCase):

    def setUp(self):
        self.movie = Movie.objects.create(
            name="Stalker",
            duration=163,
            genre="Sci-Fi",
            director="Andrei Tarkovsky"
        )
        self.room = Room.objects.create(
            name="Sala 01",
            rows=2,
            seats_per_row=2
        )
        self.session = Session.objects.create(
            movie=self.movie,
            room=self.room,
            starts_at=timezone.now() + timedelta(days=1)
        )
        self.staff_user = User.objects.create_user(
            username='staff_user',
            email='staff@tarkovsky.com',
            password='123',
            is_staff=True
        )
        self.common_user = User.objects.create_user(
            username='common_user',
            email='user@tarkovsky.com',
            password='123'
        )
        self.list_by_movie_url = f'/sessions/movie/{self.movie.id}/'
        self.seat_map_url = f'/sessions/{self.session.id}/seats/'

    def test_reserve_seat_success(self):
        cache.clear()
        self.client.force_authenticate(user=self.common_user)

        seat = Seat.objects.filter(session=self.session).first()
        seat.status = OrderStatus.AVAILABLE
        seat.save()

        url = f'/sessions/{self.session.id}/seats/{seat.id}/reserve/'
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_by_movie_is_public(self):
        response = self.client.get(self.list_by_movie_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_session_requires_staff(self):
        self.client.force_authenticate(user=self.common_user)
        data = {
            "movie": self.movie.id,
            "room": self.room.id,
            "starts_at": timezone.now() + timedelta(days=2)
        }
        response = self.client.post('/sessions/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_seat_map_requires_authentication(self):
        self.client.force_authenticate(user=self.common_user)
        response = self.client.get(self.seat_map_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)