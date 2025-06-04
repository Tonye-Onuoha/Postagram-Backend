from rest_framework.test import APITestCase
from rest_framework import status
from core.users.models import User
from core.posts.models import Post
from core.comments.models import Comment


class CommentsViewsTest(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email="test@gmail.com", username="test_user", password="test_password", first_name="Test", last_name="User")
        self.user2 = User.objects.create_user(email="otheruser@gmail.com", username="other_user", password="other_password", first_name="Other", last_name="User")
        self.post = Post.objects.create(author=self.user1, body="Test Post Body")
        self.user1_comment = Comment.objects.create(author=self.user1, post=self.post, body="Test User Comment Body")
        self.user2_comment = Comment.objects.create(author=self.user2, post=self.post, body="Other User Comment Body")

    def test_list_comments_for_anonymous_user(self):
        url = f'/api/core/posts/{self.post.public_id}/comment/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # retrieve oldest comment in response data.
        response_data = response.data[-1]
        self.assertTrue('author' in response_data)
        self.assertTrue('post' in response_data)
        self.assertTrue('body' in response_data)
        # assert two comments exist on this post.
        self.assertEqual(len(response.data), 2)

    def test_list_comments_for_authenticated_user(self):
        url = '/api/core/auth/token/'
        # login user to retrieve token.
        response = self.client.post(url, data={"email":"test@gmail.com", "password":"test_password"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)
        # use access token with authorization header for subsequent requests.
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])
        url = f'/api/core/posts/{self.post.public_id}/comment/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # retrieve oldest comment in response data.
        response_data = response.data[-1]
        self.assertTrue('author' in response_data)
        self.assertTrue('post' in response_data)
        self.assertTrue('body' in response_data)
        # assert two comments exist on this post.
        self.assertEqual(len(response.data), 2)

    def test_anonymous_user_cannot_create_comments(self):
        url = f'/api/core/posts/{self.post.public_id}/comment/'
        comment_data = {
            "post": self.post.public_id,
            "author": self.user1.public_id,
            "body": "Anonymous Comment Body",
            }
        response = self.client.post(url, data=comment_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_create_comments(self):
        url = '/api/core/auth/token/'
        # login user to retrieve token.
        response = self.client.post(url, data={"email":"test@gmail.com", "password":"test_password"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)
        # use access token with authorization header for subsequent requests.
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])
        url = f'/api/core/posts/{self.post.public_id}/comment/'
        comment_data = {
            "post": self.post.public_id,
            "author": self.user1.public_id,
            "body": "Authenticated Comment Body",
            }
        response = self.client.post(url, data=comment_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_retrieve_comment_for_anonymous_user(self):
        url = f'/api/core/posts/{self.post.public_id}/comment/{self.user1_comment.public_id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_comment_for_authenticated_user(self):
        url = '/api/core/auth/token/'
        # login user to retrieve token.
        response = self.client.post(url, data={"email":"test@gmail.com", "password":"test_password"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)
        # use access token with authorization header for subsequent requests.
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])
        url = f'/api/core/posts/{self.post.public_id}/comment/{self.user1_comment.public_id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_anonymous_user_cannot_update_comments(self):
        url = f'/api/core/posts/{self.post.public_id}/comment/{self.user1_comment.public_id}/'
        comment_data = {
            "post": self.post.public_id,
            "author": self.user1.public_id,
            "body": "Anonymous Comment Body",
            }
        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_lacks_object_permissions_for_comment_updates(self):
        url = '/api/core/auth/token/'
        # login user to retrieve token.
        response = self.client.post(url, data={"email":"test@gmail.com", "password":"test_password"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)
        # use access token with authorization header for subsequent requests.
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])
        url = f'/api/core/posts/{self.post.public_id}/comment/{self.user2_comment.public_id}/'
        comment_data = {
            "post": self.post.public_id,
            "author": self.user1.public_id,
            "body": "Authenticated Comment Body",
            }
        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_user_can_update_comments(self):
        url = '/api/core/auth/token/'
        # login user to retrieve token.
        response = self.client.post(url, data={"email":"test@gmail.com", "password":"test_password"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)
        # use access token with authorization header for subsequent requests.
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])
        url = f'/api/core/posts/{self.post.public_id}/comment/{self.user1_comment.public_id}/'
        comment_data = {
            "post": self.post.public_id,
            "author": self.user1.public_id,
            "body": "Authenticated Comment Body",
            }
        response = self.client.put(url, data=comment_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_anonymous_user_cannot_delete_comments(self):
        url = f'/api/core/posts/{self.post.public_id}/comment/{self.user1_comment.public_id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_lacks_object_permissions_to_delete_comment(self):
        new_user = self.user2 = User.objects.create_user(email="newuser@gmail.com", username="new_user", password="new_password", first_name="New", last_name="User")
        url = '/api/core/auth/token/'
        # login user to retrieve token.
        response = self.client.post(url, data={"email":"newuser@gmail.com", "password":"new_password"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)
        # use access token with authorization header for subsequent requests.
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])
        url = f'/api/core/posts/{self.post.public_id}/comment/{self.user2_comment.public_id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_user_can_delete_comments(self):
        url = '/api/core/auth/token/'
        # login user to retrieve token.
        response = self.client.post(url, data={"email":"test@gmail.com", "password":"test_password"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)
        # use access token with authorization header for subsequent requests.
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])
        url = f'/api/core/posts/{self.post.public_id}/comment/{self.user1_comment.public_id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_authenticated_user_can_like_a_comment(self):
        # login user to retrieve token.
        url = '/api/core/auth/token/'
        response = self.client.post(url, data={"email":"otheruser@gmail.com", "password":"other_password"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)
        # use access token with authorization header for subsequent requests.
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])
        url = f'/api/core/posts/{self.post.public_id}/comment/{self.user1_comment.public_id}/like/'
        response = self.client.get(url)
        # assert that authorized user has liked a comment.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['liked'])
        self.assertEqual(response.data['likes_count'], 1)

    def test_authenticated_user_can_unlike_a_comment(self):
        # let user2 like a comment from user1.
        self.user2.like_comment(self.user1_comment)
        # assert user2 has liked a comment.
        self.assertTrue(self.user2.comments_liked.contains(self.user1_comment))
        # login user to retrieve token.
        url = '/api/core/auth/token/'
        response = self.client.post(url, data={"email":"otheruser@gmail.com", "password":"other_password"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)
        # use access token with authorization header for subsequent requests.
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + response.data['access'])
        url = f'/api/core/posts/{self.post.public_id}/comment/{self.user1_comment.public_id}/remove_like/'
        response = self.client.get(url)
        # assert that authorized user has unliked a comment.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['liked'])
        self.assertEqual(response.data['likes_count'], 0)

