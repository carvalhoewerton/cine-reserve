from rest_framework import viewsets, status
from rest_framework.response import Response
from apps.user.serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny

class UserViewSet(viewsets.ViewSet):

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]

    def create(self, request):
        serializer = UserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(
            {'message': 'User successfully created', 'data': serializer.data},
            status=status.HTTP_201_CREATED)

