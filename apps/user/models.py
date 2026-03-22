from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.core.models import AbstractModel


class User(AbstractUser, AbstractModel):
    email = models.EmailField(unique=True)

