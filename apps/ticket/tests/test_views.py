from rest_framework.test import APITestCase
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.core.cache import cache
from unittest.mock import patch
from apps.movie.models import Movie
from apps.room.models import Room
from apps.session.models import Session
from apps.seat.models import Seat, OrderStatus, SeatReservation
from apps.ticket.models import Ticket

User = get_user_model()


class TicketViewSetTests(APITestCase):

    def setUp(self):
        cache.clear()
        self.movie = Movie.objects.create(
            name="The Mirror",
            duration=107,
            genre="Drama",
            director="Andrei Tarkovsky"
        )
        self.room = Room.objects.create(
            name="Sala Espelho",
            rows=2,
            seats_per_row=2
        )
        self.session = Session.objects.create(
            movie=self.movie,
            room=self.room,
            starts_at=timezone.now() + timedelta(days=1)
        )
        self.user = User.objects.create_user(
            username='tarkovsky_fan',
            email='fan@tarkovsky.com',
            password='123'
        )
        self.seat = Seat.objects.filter(session=self.session).first()
        self.reservation = SeatReservation.objects.create(
            user=self.user,
            seat=self.seat
        )
        self.checkout_url = '/tickets/checkout/'
        self.my_tickets_url = '/tickets/my-tickets/'

    @patch('apps.ticket.tasks.send_ticket_email.delay')
    def test_checkout_success(self, mock_celery_task):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(self.checkout_url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ticket.objects.filter(user=self.user).count(), 1)

        self.seat.refresh_from_db()
        # O status correto após a compra deve ser PURCHASED (ou 'purchased')
        self.assertEqual(self.seat.status, OrderStatus.PURCHASED)

        self.assertFalse(SeatReservation.objects.filter(id=self.reservation.id).exists())
        mock_celery_task.assert_called_once()

    def test_checkout_no_reservations_found(self):
        other_user = User.objects.create_user(
            username='other', email='other@test.com', password='123'
        )
        self.client.force_authenticate(user=other_user)

        response = self.client.post(self.checkout_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch('apps.seat.models.SeatReservation.is_expired')
    def test_checkout_with_expired_reservation(self, mock_is_expired):
        mock_is_expired.return_value = True
        self.client.force_authenticate(user=self.user)

        response = self.client.post(self.checkout_url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_my_tickets(self):
        Ticket.objects.create(user=self.user, seat=self.seat)
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.my_tickets_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)