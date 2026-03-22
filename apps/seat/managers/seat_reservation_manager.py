from django.db import models
from django.utils import timezone


class SeatReservationManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(active=True)

    def list(self):
        return self.get_queryset()

    def get_by_id(self, id):
        return self.get_queryset().filter(id=id).first()

    def get_by_user(self, user_id):
        return self.get_queryset().filter(user_id=user_id)

    def get_expired(self):
        return self.model.objects.filter(expires_at__lt=timezone.now())

    def get_by_user_and_session(self, user_id, session_id):
        return self.get_queryset().filter(user_id=user_id,seat__session_id=session_id)

