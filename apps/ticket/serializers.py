from rest_framework import serializers
from apps.ticket.models import Ticket


class TicketSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    movie_name = serializers.CharField(source='seat.session.movie.name', read_only=True)
    movie_duration = serializers.IntegerField(source='seat.session.movie.duration', read_only=True)
    session_starts_at = serializers.SerializerMethodField()
    room_name = serializers.CharField(source='seat.session.room.name', read_only=True)
    seat_label = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = (
            'id',
            'user_name',
            'movie_name',
            'movie_duration',
            'session_starts_at',
            'room_name',
            'seat_label',
        )

    def get_session_starts_at(self, obj):
        return obj.seat.session.starts_at.strftime('%d/%m/%Y %H:%M')

    def get_seat_label(self, obj):
        return f'{obj.seat.row}{obj.seat.number}'