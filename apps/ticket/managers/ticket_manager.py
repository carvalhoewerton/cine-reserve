from django.db import models

class TicketManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(active=True)

    def get_by_user(self, user_id):
        return self.get_queryset().filter(user_id=user_id)