
from rest_framework import viewsets, status
from rest_framework.response import Response
from apps.movie.models import Movie
from apps.movie.serializers import MovieSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.decorators import permission_classes


class MovieViewSet(viewsets.ViewSet):
    pagination_class = PageNumberPagination

    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        return [IsAdminUser()]

    def list(self, request):
        movies = Movie.objects.list()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(movies, request)
        if page is not None:
            serializer = MovieSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        serializer = MovieSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': 'Movie successfully created', 'data': serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        movie = Movie.objects.get_by_id(pk)
        if not movie:
            return Response({'error': 'Movie not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = MovieSerializer(movie)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        movie = Movie.objects.get_by_id(pk)
        if not movie:
            return Response({'error': 'Movie not found'}, status=status.HTTP_404_NOT_FOUND)
        movie.delete()
        return Response(
            {'message': 'Movie successfully deleted'},
            status=status.HTTP_200_OK
        )