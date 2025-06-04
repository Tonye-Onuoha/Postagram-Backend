from django.test import TestCase
from core.users.models import User
from core.posts.models import Post

# Create your tests here.
class PostModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="test@gmail.com", username="test_user", password="test_password", first_name="Test", last_name="User")

    def test_create_post(self):
        post = Post.objects.create(author=self.user, body="Test Post Body")
        expected_username = "test_user"
        self.assertEqual(post.author.username, expected_username)
        self.assertEqual(post.body, "Test Post Body")
