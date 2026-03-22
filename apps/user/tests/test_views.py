from rest_framework.test import APITestCase
from rest_framework import status
from apps.user.models import User


class UserViewTests(APITestCase):

    def setUp(self):
        self.password = 'testpass123'
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password=self.password
        )
        self.list_url = '/users/'
        self.detail_url = f'/users/{self.user.id}/'

    def test_create_user_public_access(self):
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "strongpassword123"
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.filter(username="newuser").count(), 1)
