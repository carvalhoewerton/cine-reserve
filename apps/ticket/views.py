from django.core.cache import cache
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.db import transaction


from apps.seat.models import SeatReservation
from apps.ticket.models import Ticket
from apps.ticket.serializers import TicketSerializer
from apps.ticket.tasks import send_ticket_email

class TicketViewSet(viewsets.ViewSet):
    pagination_class = PageNumberPagination

    def get_permissions(self):
        return [IsAuthenticated()]

    @action(detail=False, methods=['post'], url_path='checkout')
    def checkout(self, request):
        user = request.user

        with transaction.atomic():
            reservations = SeatReservation.objects.get_by_user(user.id).select_for_update()
            if not reservations.exists():
                return Response({'error': 'No reservations found'}, status=status.HTTP_404_NOT_FOUND)

            tickets = []
            purchased_seats = []

            for reservation in reservations:
                if reservation.is_expired():
                    continue

                seat = reservation.seat
                cache.delete(f'seat_lock_{seat.id}')
                reservation.delete()
                seat.purchase()
                purchased_seats.append(seat)
                tickets.append(Ticket(user=user, seat=seat))

            if not tickets:
                return Response({'error': 'All reservations have expired'}, status=status.HTTP_400_BAD_REQUEST)

            Ticket.objects.bulk_create(tickets)

        created_tickets = Ticket.objects.filter(user=user, seat__in=purchased_seats)
        serializer = TicketSerializer(created_tickets, many=True)

        send_ticket_email.delay(
            user_email=user.email,
            user_name=user.username,
            tickets_data=list(serializer.data)
        )

        return Response(
            {
                'message': f'{len(tickets)} ticket(s) successfully generated',
                'data': serializer.data
            },
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=['get'], url_path='my-tickets')
    def get_by_user(self, request):
        tickets = Ticket.objects.get_by_user(request.user.id)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(tickets, request, view=self)

        if page is not None:
            serializer = TicketSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = TicketSerializer(tickets, many=True)
        return Response(serializer.data)


