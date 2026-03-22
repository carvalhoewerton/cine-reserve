from apps.movie.models import Movie
from rest_framework import serializers

class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ('id', 'name', 'duration', 'genre', 'director', 'description')