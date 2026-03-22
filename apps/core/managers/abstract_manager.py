from django.db import models

class AbstractManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(active=True)

    def list(self):
        return self.get_queryset()

    def get_by_id(self, id: int):
        return self.get_queryset().filter(id=id).first()