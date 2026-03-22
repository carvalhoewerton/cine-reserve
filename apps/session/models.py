from datetime import timedelta
from django.db import models
from django.core.exceptions import ValidationError
from apps.core.models import AbstractModel
from apps.seat.models import Seat
from apps.session.managers.session_manager import SessionManager


class Session(AbstractModel):
    movie = models.ForeignKey('movie.Movie',on_delete=models.PROTECT,related_name='sessions')
    room = models.ForeignKey('room.Room',on_delete=models.PROTECT,related_name='sessions')
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField(editable=False)

    objects = SessionManager()

    class Meta:
        ordering = ['starts_at']

    def save(self, *args, **kwargs):
        self.ends_at = self.starts_at + timedelta(minutes=self.movie.duration)

        already_exist = Session.objects.filter(
            room=self.room,
            starts_at__lt=self.ends_at,
            ends_at__gt=self.starts_at,
            active=True
        ).exclude(id=self.id).exists()

        if already_exist:
            raise ValidationError('Room already has a session in this time slot')

        is_new = self._state.adding
        super().save(*args, **kwargs)

        if is_new:
            seats = []
            for row in range(self.room.rows):
                row_letter = chr(65 + row)
                for number in range(1, self.room.seats_per_row + 1):
                    seats.append(Seat(
                        session=self,
                        row=row_letter,
                        number=number,
                    ))
            Seat.objects.bulk_create(seats)