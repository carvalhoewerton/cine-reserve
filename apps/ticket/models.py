from django.db import models
from apps.core.models import AbstractModel
from apps.ticket.managers.ticket_manager import TicketManager


class Ticket(AbstractModel):
    user = models.ForeignKey('user.User',on_delete=models.PROTECT,related_name='tickets')
    seat = models.OneToOneField('seat.Seat',on_delete=models.PROTECT,related_name='ticket')

    objects = TicketManager()

