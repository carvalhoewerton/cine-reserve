from celery import shared_task
from django.core.cache import cache


@shared_task
def release_expired_seats():
    from apps.seat.models import SeatReservation, OrderStatus

    expired = SeatReservation.objects.get_expired()
    for reservation in expired:
        seat = reservation.seat
        seat.status = OrderStatus.AVAILABLE
        seat.save()
        cache.delete(f'seat_lock_{seat.id}')
        reservation.delete()