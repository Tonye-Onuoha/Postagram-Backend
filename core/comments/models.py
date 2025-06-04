from django.db import models
from core.abstract.models import AbstractModel, AbstractManager

# Create your models here.
class CommentManager(AbstractManager):
    pass

class Comment(AbstractModel):
    post = models.ForeignKey("core_posts.Post", on_delete=models.PROTECT)
    author = models.ForeignKey("core_users.User", on_delete=models.PROTECT)
    body = models.TextField()
    edited = models.BooleanField(default=False)

    objects = CommentManager()

    def __str__(self):
        return self.author.name
