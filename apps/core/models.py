from django.db import models

from apps.core.managers.abstract_manager import AbstractManager


class AbstractModel(models.Model):
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = AbstractManager()

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        self.active = False
        self.save()