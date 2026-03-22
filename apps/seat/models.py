from django.utils import timezone
from datetime import timedelta

from django.db import models

from apps.core.models import AbstractModel
from apps.seat.managers.seat_manager import SeatManager
from apps.seat.managers.seat_reservation_manager import SeatReservationManager


class OrderStatus(models.TextChoices):
    AVAILABLE = 'available', 'Available'
    HOLD = 'hold', 'Hold'
    PURCHASED = 'purchased', 'Purchased'

class Seat(AbstractModel):
    row = models.CharField(max_length=2)
    number = models.IntegerField()
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.AVAILABLE)
    session = models.ForeignKey('session.Session', on_delete=models.CASCADE, related_name='seats')

    objects = SeatManager()

    class Meta:
        ordering = ['row', 'number']
        unique_together = ('row', 'number','session')


    def purchase(self):
        self.status = OrderStatus.PURCHASED
        self.save()

class SeatReservation(AbstractModel):
    seat = models.ForeignKey('seat.Seat',on_delete=models.CASCADE,related_name='reservations')
    user = models.ForeignKey('user.User',on_delete=models.CASCADE,related_name='reservations')
    expires_at = models.DateTimeField()

    objects = SeatReservationManager()

    def save(self, *args, **kwargs):
        self.expires_at = timezone.now() + timedelta(minutes=10)
        self.seat.status = OrderStatus.HOLD
        self.seat.save()
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.expires_at


