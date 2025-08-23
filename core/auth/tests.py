from rest_framework.test import APITestCase
from rest_framework import status
from core.users.models import User

# Create your tests here.
class AuthenticationViewTests(APITestCase):
    """
    This subclass contains tests for user-registration, login and logout functionality.
    """
    def test_register_user(self):
        url = '/api/core/auth/register/'
        user_data = {
            "username": "johndoe",
            "email": "johndoe@yopmail.com",
            "password": "test_password",
            "first_name": "John",
            "last_name": "Doe"
            }
        response = self.client.post(url, data=user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)

    def test_login_user(self):
        # create new user.
        User.objects.create_user(email="test@gmail.com", username="test_user", password="test_password", first_name="Test", last_name="User")
        url = '/api/core/auth/login/'
        # login user to retrieve token.
        response = self.client.post(url, data={"email":"test@gmail.com", "password":"test_password"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)

    def test_refresh_token(self):
        # create new user.
        User.objects.create_user(email="test@gmail.com", username="test_user", password="test_password", first_name="Test", last_name="User")
        url = '/api/core/auth/login/'
        # login user to retrieve token.
        response = self.client.post(url, data={"email":"test@gmail.com", "password":"test_password"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)
        # use refresh-token to retrieve new access-token.
        url = '/api/core/auth/token/refresh/'
        response = self.client.post(url, data={"refresh":response.data["refresh"]})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)

    def test_logout_user_with_valid_refresh_token(self):
        # create new user.
        User.objects.create_user(email="test@gmail.com", username="test_user", password="test_password", first_name="Test", last_name="User")
        url = '/api/core/auth/login/'
        # login user to retrieve token.
        response = self.client.post(url, data={"email":"test@gmail.com", "password":"test_password"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)
        # use access token with authorization header for subsequent requests.
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + response.data["access"])
        # logout the user to blacklist token.
        url = '/api/core/auth/logout/'
        refresh_token = response.data["refresh"]
        response = self.client.post(url, data={"refresh":refresh_token})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_logout_user_with_invalid_refresh_token(self):
        # create new user.
        User.objects.create_user(email="test@gmail.com", username="test_user", password="test_password", first_name="Test", last_name="User")
        url = '/api/core/auth/login/'
        # login user to retrieve token.
        response = self.client.post(url, data={"email":"test@gmail.com", "password":"test_password"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)
        # use access token with authorization header for subsequent requests.
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + response.data["access"])
        # logout the user to blacklist token.
        url = '/api/core/auth/logout/'
        INVALID_TOKEN = "INVALID_REFRESH_TOKEN"
        response = self.client.post(url, data={"refresh":INVALID_TOKEN})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


