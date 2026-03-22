from rest_framework.decorators import action
from django.core.exceptions import ValidationError
from rest_framework import viewsets, status
from rest_framework.response import Response

from apps.seat.models import Seat, OrderStatus

from apps.seat.models import SeatReservation
from apps.seat.serializers import SeatSerializer
from apps.session.models import Session
from apps.session.serializers import SessionSerializer, SessionByMovieSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny

class SessionViewSet(viewsets.ViewSet):
    pagination_class = PageNumberPagination

    def get_permissions(self):
        if self.action == 'list_by_movie':
            return [AllowAny()]
        if self.action == 'create':
            return [IsAdminUser()]
        return [IsAuthenticated()]

    @action(detail=True, methods=['get'], url_path='seats')
    def seat_map(self, request, pk=None):
        session = Session.objects.get_by_id(pk)
        if not session:
            return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)

        seats = Seat.objects.get_by_session(pk)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(seats, request)
        if page is not None:
            serializer = SeatSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = SeatSerializer(seats, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='movie/(?P<movie_id>[^/.]+)')
    def list_by_movie(self, request, movie_id=None):
        sessions = Session.objects.get_by_movie(movie_id)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(sessions, request)
        if page is not None:
            serializer = SessionByMovieSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = SessionByMovieSerializer(sessions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        serializer = SessionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            serializer.save()
        except ValidationError as e:
            return Response({'error': e.message}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {'message': 'Session successfully created', 'data': serializer.data},
            status=status.HTTP_201_CREATED)


    @action(detail=True, methods=['post'], url_path='seats/(?P<seat_id>[^/.]+)/reserve')
    def reserve(self, request, pk=None, seat_id=None):
        from django.core.cache import cache

        user = request.user

        seat = Seat.objects.get_by_id(seat_id)
        if not seat:
            return Response({'error': 'Seat not found'}, status=status.HTTP_404_NOT_FOUND)

        if seat.status != OrderStatus.AVAILABLE:
            return Response({'error': 'Seat is not available'}, status=status.HTTP_400_BAD_REQUEST)

        lock_key = f'seat_lock_{seat_id}'
        if cache.get(lock_key):
            return Response({'error': 'Seat is already being reserved'}, status=status.HTTP_400_BAD_REQUEST)

        cache.set(lock_key, user.id, timeout=600)
        SeatReservation.objects.create(seat=seat, user=user)

        return Response({'message': 'Seat successfully reserved'}, status=status.HTTP_200_OK)

