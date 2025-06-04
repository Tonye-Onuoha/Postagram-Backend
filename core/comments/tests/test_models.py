from django.test import TestCase
from core.users.models import User
from core.posts.models import Post
from core.comments.models import Comment

# Create your tests here.
class CommentModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="test@gmail.com", username="test_user", password="test_password", first_name="Test", last_name="User")
        self.post = Post.objects.create(author=self.user, body="Test Post Body")

    def test_create_comment(self):
        comment = Comment.objects.create(author=self.user, post=self.post, body="Test Comment Body")
        expected_username = "test_user"
        self.assertEqual(comment.author.username, expected_username)
        self.assertEqual(comment.post.body, "Test Post Body")
        self.assertEqual(comment.body, "Test Comment Body")
