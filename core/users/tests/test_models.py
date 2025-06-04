from django.test import TestCase
from core.users.models import User

# Create your tests here.
def create_new_user(email, username, password, **kwargs):
    return User.objects.create_user(email, username, password, **kwargs)

def create_new_superuser(email, username, password, **kwargs):
    return User.objects.create_superuser(email, username, password, **kwargs)

class UserModelTests(TestCase):
    def test_create_user(self):
        user_data = {
            "username": "test_user",
            "email": "test@gmail.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "test_password"
            }
        user = create_new_user(user_data["email"], user_data["username"], user_data["password"], first_name=user_data["first_name"], last_name=user_data["last_name"])
        self.assertEqual(user.username, user_data["username"])
        self.assertEqual(user.email, user_data["email"])
        self.assertEqual(user.first_name, user_data["first_name"])
        self.assertEqual(user.last_name, user_data["last_name"])

    def test_create_superuser(self):
        user_data = {
            "username": "test_user",
            "email": "test@gmail.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "test_password"
            }
        user = create_new_superuser(user_data["email"], user_data["username"], user_data["password"], first_name=user_data["first_name"], last_name=user_data["last_name"])
        self.assertEqual(user.username, user_data["username"])
        self.assertEqual(user.email, user_data["email"])
        self.assertEqual(user.first_name, user_data["first_name"])
        self.assertEqual(user.last_name, user_data["last_name"])
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

