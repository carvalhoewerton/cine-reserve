from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from apps.movie.models import Movie
from apps.room.models import Room
from apps.session.models import Session
from apps.seat.models import Seat
from apps.ticket.models import Ticket

User = get_user_model()


class TicketModelTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='viewer',
            email='viewer@tarkovsky.com',
            password='123'
        )
        self.movie = Movie.objects.create(
            name="Nostalgia",
            duration=125,
            genre="Drama",
            director="Tarkovsky"
        )
        self.room = Room.objects.create(
            name="Sala 03",
            rows=5,
            seats_per_row=5
        )
        self.session = Session.objects.create(
            movie=self.movie,
            room=self.room,
            starts_at=timezone.now() + timedelta(days=1)
        )
        self.seat = Seat.objects.filter(session=self.session).first()

    def test_create_ticket_success(self):
        ticket = Ticket.objects.create(user=self.user, seat=self.seat)
        self.assertEqual(Ticket.objects.count(), 1)
        self.assertEqual(ticket.user, self.user)

    def test_ticket_onetoone_seat_constraint(self):
        Ticket.objects.create(user=self.user, seat=self.seat)
        user2 = User.objects.create_user(
            username='viewer2',
            email='viewer2@tarkovsky.com',
            password='123'
        )
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Ticket.objects.create(user=user2, seat=self.seat)

    def test_ticket_soft_delete(self):
        ticket = Ticket.objects.create(user=self.user, seat=self.seat)
        ticket.delete()

        self.assertFalse(Ticket.objects.filter(id=ticket.id).exists())

        ticket.refresh_from_db()
        self.assertFalse(ticket.active)

    def test_manager_get_by_user(self):
        ticket = Ticket.objects.create(user=self.user, seat=self.seat)
        user_tickets = Ticket.objects.get_by_user(self.user.id)
        self.assertIn(ticket, user_tickets)