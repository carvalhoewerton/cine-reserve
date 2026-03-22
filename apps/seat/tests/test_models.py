from rest_framework.test import APITestCase
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from apps.movie.models import Movie
from apps.room.models import Room
from apps.session.models import Session
from apps.seat.models import Seat, OrderStatus, SeatReservation

User = get_user_model()


class SeatModelTests(APITestCase):

    def setUp(self):
        self.movie = Movie.objects.create(
            name="Solaris",
            duration=167,
            genre="Sci-Fi",
            director="Andrei Tarkovsky"
        )
        self.room = Room.objects.create(
            name="Sala Solaris",
            rows=2,
            seats_per_row=2
        )
        self.session = Session.objects.create(
            movie=self.movie,
            room=self.room,
            starts_at=timezone.now() + timedelta(days=1)
        )
        self.user = User.objects.create_user(
            username='kelvin',
            email='kelvin@solaris.com',
            password='123'
        )
        self.seat = Seat.objects.filter(session=self.session).first()

    def test_seat_default_status(self):
        self.assertEqual(self.seat.status, OrderStatus.AVAILABLE)

    def test_seat_purchase_method(self):
        self.seat.purchase()
        self.assertEqual(self.seat.status, OrderStatus.PURCHASED)

    def test_seat_reservation_updates_seat_status(self):
        SeatReservation.objects.create(
            user=self.user,
            seat=self.seat
        )
        self.seat.refresh_from_db()
        self.assertEqual(self.seat.status, OrderStatus.HOLD)

    def test_seat_reservation_is_expired(self):
        reservation = SeatReservation.objects.create(
            user=self.user,
            seat=self.seat
        )
        self.assertFalse(reservation.is_expired())

        past_date = timezone.now() - timedelta(minutes=1)
        SeatReservation.objects.filter(id=reservation.id).update(expires_at=past_date)

        reservation.refresh_from_db()
        self.assertTrue(reservation.is_expired())

    def test_seat_manager_get_by_session(self):
        seats = Seat.objects.get_by_session(self.session.id)
        self.assertIn(self.seat, seats)

    def test_reservation_manager_get_by_user(self):
        reservation = SeatReservation.objects.create(
            user=self.user,
            seat=self.seat
        )
        reservations = SeatReservation.objects.get_by_user(self.user.id)
        self.assertIn(reservation, reservations)

    def test_reservation_manager_get_expired(self):
        reservation = SeatReservation.objects.create(
            user=self.user,
            seat=self.seat
        )
        past_date = timezone.now() - timedelta(minutes=20)
        SeatReservation.objects.filter(id=reservation.id).update(expires_at=past_date)

        expired_reservations = SeatReservation.objects.get_expired()
        self.assertIn(reservation, expired_reservations)