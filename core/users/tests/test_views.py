from rest_framework.test import APITestCase
from rest_framework import status
from core.users.models import User


class UserViewsTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email="test@gmail.com", username="test_user", password="test_password", first_name="Test", last_name="User")
        self.user2 = User.objects.create_user(email="otheruser@gmail.com", username="other_user", password="other_password", first_name="Other", last_name="User")

    def test_hide_users_for_anonymous_user(self):
        url = '/api/core/users/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_users_for_authenticated_user(self):
        url = '/api/core/auth/token/'
        # login user to retrieve token.
        response = self.client.post(url, data={"email":"test@gmail.com", "password":"test_password"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)
        # use access token with authorization header for subsequent requests.
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])
        url = '/api/core/users/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # retrieve oldest comment in response data.
        response_data = response.data[-1]
        self.assertTrue('first_name' in response_data)
        self.assertTrue('last_name' in response_data)
        self.assertTrue('username' in response_data)
        self.assertEqual(response_data['username'], 'test_user')
        # assert two users exist.
        self.assertEqual(len(response.data), 2)

    def test_hide_user_for_anonymous_user(self):
        url = f'/api/core/users/{self.user1.public_id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_user_for_authenticated_user(self):
        url = '/api/core/auth/token/'
        # login user to retrieve token.
        response = self.client.post(url, data={"email":"test@gmail.com", "password":"test_password"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)
        # use access token with authorization header for subsequent requests.
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])
        url = f'/api/core/users/{self.user1.public_id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cannot_create_new_users_via_POST_request(self):
        url = '/api/core/auth/token/'
        # login user to retrieve token.
        response = self.client.post(url, data={"email":"test@gmail.com", "password":"test_password"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)
        # use access token with authorization header for subsequent requests.
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])
        url = '/api/core/users/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_anonymous_user_cannot_update_a_user(self):
        url = f'/api/core/users/{self.user1.public_id}/'
        user_data = {
            "first_name": "New"
        }
        response = self.client.patch(url, data=user_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_cannot_update_another_user_object(self):
        url = '/api/core/auth/token/'
        # login user to retrieve token.
        response = self.client.post(url, data={"email":"test@gmail.com", "password":"test_password"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)
        # use access token with authorization header for subsequent requests.
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])
        url = f'/api/core/users/{self.user2.public_id}/'
        user_data = {
            "first_name": "New"
        }
        response = self.client.patch(url, data=user_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_user_can_update_own_user_object(self):
        url = '/api/core/auth/token/'
        # login user to retrieve token.
        response = self.client.post(url, data={"email":"test@gmail.com", "password":"test_password"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)
        # use access token with authorization header for subsequent requests.
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])
        url = f'/api/core/users/{self.user1.public_id}/'
        user_data = {
            "first_name": "New"
        }
        response = self.client.patch(url, data=user_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
