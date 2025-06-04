from rest_framework.test import APITestCase
from rest_framework import status
from core.users.models import User
from core.posts.models import Post

# Create your tests here.
class PostViewsTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email="test@gmail.com", username="test_user", password="test_password", first_name="Test", last_name="User")
        self.user2 = User.objects.create_user(email="otheruser@gmail.com", username="other_user", password="other_password", first_name="Other", last_name="User")
        self.post = Post.objects.create(author=self.user1, body="Test Post Body")
        self.post2 = Post.objects.create(author=self.user1, body="Test Post Body 2")

    def test_list_posts_for_anonymous_user(self):
        url = '/api/core/posts/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # retrieve first item in response data.
        response_data = response.data[0]
        self.assertTrue('author' in response_data)
        self.assertTrue('body' in response_data)
        self.assertEqual(response_data['author']['username'], 'test_user')
        self.assertEqual(response_data['body'], 'Test Post Body 2')

    def test_list_posts_for_authenticated_user(self):
        # login user to retrieve token.
        url = '/api/core/auth/token/'
        response = self.client.post(url, data={"email":"test@gmail.com", "password":"test_password"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)
        # use access token with authorization header for subsequent requests.
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])
        url = '/api/core/posts/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # retrieve first item in response data.
        response_data = response.data[0]
        self.assertTrue('author' in response_data)
        self.assertTrue('body' in response_data)
        self.assertEqual(response_data['author']['username'], 'test_user')
        self.assertEqual(response_data['body'], 'Test Post Body 2')

    def test_retrieve_posts_by_authenticated_user(self):
        # login user to retrieve token.
        url = '/api/core/auth/token/'
        response = self.client.post(url, data={"email":"test@gmail.com", "password":"test_password"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)
        # use access token with authorization header for subsequent requests.
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])
        url = f'/api/core/posts/?author_public_id={self.user1.public_id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # assert user1 has two posts.
        self.assertEqual(len(response.data), 2)

    def test_anonymous_user_cannot_create_posts(self):
        url = '/api/core/posts/'
        post_data = {
            "body": "Anonymous Post Body",
            "author": self.user1.public_id,
            }
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_create_posts(self):
        # login user to retrieve token.
        url = '/api/core/auth/token/'
        response = self.client.post(url, data={"email":"test@gmail.com", "password":"test_password"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)
        # use access token with authorization header for subsequent requests.
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])
        url = '/api/core/posts/'
        post_data = {
            "body": "Authenticated Post Body",
            "author": self.user1.public_id,
            }
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_retrieve_post_for_anonymous_user(self):
        url = f'/api/core/posts/{self.post.public_id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_post_for_authenticated_user(self):
        # login user to retrieve token.
        url = '/api/core/auth/token/'
        response = self.client.post(url, data={"email":"test@gmail.com", "password":"test_password"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)
        # use access token with authorization header for subsequent requests.
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])
        url = f'/api/core/posts/{self.post.public_id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_post_with_invalid_UUID(self):
        # login user to retrieve token.
        url = '/api/core/auth/token/'
        response = self.client.post(url, data={"email":"test@gmail.com", "password":"test_password"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)
        # use access token with authorization header for subsequent requests.
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])
        url = f'/api/core/posts/INVALID_UUID404/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data[0]), 'INVALID_UUID404 is not a valid UUID')

    def test_retrieve_post_that_does_not_exist(self):
        # login user to retrieve token.
        url = '/api/core/auth/token/'
        response = self.client.post(url, data={"email":"test@gmail.com", "password":"test_password"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)
        # use access token with authorization header for subsequent requests.
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])
        url = f'/api/core/posts/{self.user2.public_id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data[0]), f'There is no post with public id "{self.user2.public_id}"')

    def test_anonymous_user_cannot_update_posts(self):
        url = f'/api/core/posts/{self.post.public_id}/'
        post_data = {
            "body": "Updated Anonymous Post Body",
            "author": self.post.author.public_id,
            }
        response = self.client.put(url, data=post_data)
        # assert that unauthorized user cannot update the post.
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_lacks_object_permissions_for_post_updates(self):
        # login user to retrieve token.
        url = '/api/core/auth/token/'
        response = self.client.post(url, data={"email":"otheruser@gmail.com", "password":"other_password"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)
        # use access token with authorization header for subsequent requests.
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])
        url = f'/api/core/posts/{self.post.public_id}/'
        post_data = {
            "body": "Updated Authenticated Post Body",
            "author": self.post.author.public_id,
            }
        response = self.client.put(url, data=post_data)
        # assert that user does not have the required object permission.
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_user_can_update_posts(self):
        # login user to retrieve token.
        url = '/api/core/auth/token/'
        response = self.client.post(url, data={"email":"test@gmail.com", "password":"test_password"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)
        # use access token with authorization header for subsequent requests.
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])
        url = f'/api/core/posts/{self.post.public_id}/'
        post_data = {
            "body": "Updated Authenticated Post Body",
            "author": self.post.author.public_id,
            }
        response = self.client.put(url, data=post_data)
        # assert that authorized user with correct object permissions can update posts.
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_anonymous_user_cannot_delete_posts(self):
        url = f'/api/core/posts/{self.post.public_id}/'
        response = self.client.delete(url)
        # assert that unauthorized user cannot delete the post.
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_lacks_object_permissions_for_post_deletions(self):
        # login user to retrieve token.
        url = '/api/core/auth/token/'
        response = self.client.post(url, data={"email":"otheruser@gmail.com", "password":"other_password"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)
        # use access token with authorization header for subsequent requests.
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])
        url = f'/api/core/posts/{self.post.public_id}/'
        response = self.client.delete(url)
        # assert that user does not have the required object permission.
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_user_can_delete_posts(self):
        # login user to retrieve token.
        url = '/api/core/auth/token/'
        response = self.client.post(url, data={"email":"test@gmail.com", "password":"test_password"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)
        # use access token with authorization header for subsequent requests.
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])
        url = f'/api/core/posts/{self.post.public_id}/'
        response = self.client.delete(url)
        # assert that authorized user with correct object permission can delete posts.
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_authenticated_user_can_like_a_post(self):
        # login user to retrieve token.
        url = '/api/core/auth/token/'
        response = self.client.post(url, data={"email":"otheruser@gmail.com", "password":"other_password"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)
        # use access token with authorization header for subsequent requests.
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])
        url = f'/api/core/posts/{self.post.public_id}/like/'
        response = self.client.get(url)
        # assert that authorized user has liked a post.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['liked'])
        self.assertEqual(response.data['likes_count'], 1)

    def test_authenticated_user_can_unlike_a_post(self):
        # let user2 like a post from user1.
        self.user2.like_post(self.post)
        # assert user2 has liked a post.
        self.assertTrue(self.user2.posts_liked.contains(self.post))
        # login user to retrieve token.
        url = '/api/core/auth/token/'
        response = self.client.post(url, data={"email":"otheruser@gmail.com", "password":"other_password"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)
        # use access token with authorization header for subsequent requests.
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])
        url = f'/api/core/posts/{self.post.public_id}/remove_like/'
        response = self.client.get(url)
        # assert that authorized user has unliked a post.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['liked'])
        self.assertEqual(response.data['likes_count'], 0)



