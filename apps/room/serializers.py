from rest_framework import serializers
from apps.room.models import Room


class RoomSerializer(serializers.ModelSerializer):
    total_seats = serializers.IntegerField(read_only=True)

    class Meta:
        model = Room
        fields = ('id', 'name', 'type', 'rows', 'seats_per_row', 'total_seats')
