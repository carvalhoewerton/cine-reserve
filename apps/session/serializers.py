from rest_framework import serializers

from apps.movie.serializers import MovieSerializer
from apps.room.serializers import RoomSerializer
from apps.session.models import Session
from apps.movie.models import Movie
from apps.room.models import Room


class SessionSerializer(serializers.ModelSerializer):
    starts_at = serializers.DateTimeField(input_formats=['%d/%m/%Y %H:%M'])
    ends_at = serializers.DateTimeField(read_only=True)
    movie = MovieSerializer(read_only=True)
    room = RoomSerializer(read_only=True)
    movie_id = serializers.PrimaryKeyRelatedField(
        queryset=Movie.objects.all(), source='movie', write_only=True
    )
    room_id = serializers.PrimaryKeyRelatedField(
        queryset=Room.objects.all(), source='room', write_only=True
    )

    class Meta:
        model = Session
        fields = ('id', 'movie', 'movie_id', 'room', 'room_id', 'starts_at', 'ends_at')

class SessionByMovieSerializer(serializers.ModelSerializer):
    room_name = serializers.CharField(source='room.name', read_only=True)
    starts_at = serializers.SerializerMethodField()
    ends_at = serializers.SerializerMethodField()

    class Meta:
        model = Session
        fields = ('id', 'room_name', 'starts_at', 'ends_at')

    def get_starts_at(self, obj):
        return obj.starts_at.strftime('%d/%m/%Y %H:%M')

    def get_ends_at(self, obj):
        return obj.ends_at.strftime('%d/%m/%Y %H:%M')