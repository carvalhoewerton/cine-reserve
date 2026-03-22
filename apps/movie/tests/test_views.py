from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.movie.models import Movie

User = get_user_model()


class MovieViewSetTests(APITestCase):

    def setUp(self):
        self.staff_user = User.objects.create_user(
            username='staff',
            email='staff@test.com',
            password='pass',
            is_staff=True
        )
        self.common_user = User.objects.create_user(
            username='user',
            email='user@test.com',
            password='pass',
            is_staff=False
        )
        self.movie = Movie.objects.create(
            name="Inception",
            duration=148,
            genre="Sci-Fi",
            director="Nolan",
            description="Dreams"
        )
        self.list_url = '/movies/'
        self.detail_url = f'/movies/{self.movie.id}/'

    def test_list_movies_public_access(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_movie_forbidden_for_common_user(self):
        self.client.force_authenticate(user=self.common_user)
        data = {
            "name": "Matrix",
            "duration": 136,
            "genre": "Action",
            "director": "Wachowski",
            "description": "Neo"
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_movie_allowed_for_staff(self):
        self.client.force_authenticate(user=self.staff_user)
        data = {
            "name": "Matrix",
            "duration": 136,
            "genre": "Action",
            "director": "Wachowski",
            "description": "Neo"
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_retrieve_movie_requires_staff(self):
        self.client.force_authenticate(user=self.common_user)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_movie_allowed_for_staff(self):
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.movie.name)

    def test_destroy_movie_forbidden_for_common_user(self):
        self.client.force_authenticate(user=self.common_user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_destroy_movie_allowed_for_staff(self):
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.movie.refresh_from_db()
        self.assertFalse(self.movie.active)

    def test_retrieve_not_found_for_staff(self):
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get('/movies/9999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)