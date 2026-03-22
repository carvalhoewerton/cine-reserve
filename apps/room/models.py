from apps.core.models import AbstractModel
from django.db import models



class RoomType(models.TextChoices):
    BASIC = 'basic', 'Basic'
    VIP = 'vip', 'VIP'
    IMAX = 'imax', 'IMAX'


ROOM_TYPE_CONFIG = {
    RoomType.BASIC: {'rows': 5, 'seats_per_row': 10},
    RoomType.VIP:   {'rows': 3, 'seats_per_row': 10}
}

class Room(AbstractModel):
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=20, choices=RoomType.choices, default=RoomType.BASIC)
    rows = models.PositiveIntegerField(editable=False)
    seats_per_row = models.PositiveIntegerField(editable=False)

    def save(self, *args, **kwargs):
        config = ROOM_TYPE_CONFIG[self.type]
        self.rows = config['rows']
        self.seats_per_row = config['seats_per_row']
        super().save(*args, **kwargs)

