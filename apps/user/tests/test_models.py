from django.test import TestCase
from apps.user.models import User

class UserModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='ewerton',
            email='ewerton@email.com',
            password='123456'
        )

    def test_create_user(self):
        self.assertEqual(self.user.username, 'ewerton')
        self.assertEqual(self.user.email, 'ewerton@email.com')
        self.assertTrue(self.user.check_password('123456'))

    def test_email_unique(self):
        with self.assertRaises(Exception):
            User.objects.create_user(
                username='ewerton2',
                email='ewerton@email.com',
                password='123456'
            )

    def test_username_unique(self):
        with self.assertRaises(Exception):
            User.objects.create_user(
                username='ewerton',
                email='ewerton2@email.com',
                password='123456'
            )

    def test_delete_deactivates_user(self):
        self.user.delete()
        updated_user = User.objects.get(id=self.user.id)
        self.assertFalse(updated_user.active)