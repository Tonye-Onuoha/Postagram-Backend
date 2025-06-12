from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
import uuid
from core.abstract.models import AbstractModel, AbstractManager


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return f"user_{instance.public_id}/{filename}"


#   You can use a custom Manager in a particular model by extending the base Manager class (models.Manager) and instantiating your custom
#   Manager in your model. There are two reasons you might want to customize a Manager: to add extra Manager methods,
#   and/or to modify the initial QuerySet the Manager returns.
#   The AbstractManager here class extends a base Manager class in its own definition.
#   To use a custom manager, you must subclass the "models.Manager" class. The "BaseUserManager" also does this by default.
#   Thus both "BaseUserManager" and AbstractManager subclass it in our code.
#   However, BaseUserManager has two methods that are important. We use one here i.e "normalize_email".
class UserManager(BaseUserManager, AbstractManager):
    def create_user(self, email, username, password=None, **kwargs):
        """Create and return a `User` with an email, phone
        number, username and password."""
        if username is None:
            raise TypeError("Users must have a username.")
        if email is None:
            raise TypeError("Users must have an email.")
        if password is None:
            raise TypeError("User must have an email.")
        user = self.model(
            username=username, email=self.normalize_email(email), **kwargs
        )  # Manager methods can access self.model to get the model class to which they’re attached.
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, username, password=None, **kwargs):
        """
        Create and return a `User` with superuser (admin)
        permissions.
        """
        if password is None:
            raise TypeError("Superusers must have a password.")
        if email is None:
            raise TypeError("Superusers must have an email.")
        if username is None:
            raise TypeError("Superusers must have a username.")
        user = self.create_user(email, username, password, **kwargs)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user


# Create your models here.
class User(AbstractModel, AbstractBaseUser, PermissionsMixin):
    """According to Django documentation AbstractBaseUser has the authentication functionality only,
    it has no actual fields, you will supply the fields to use when you subclass."""

    """AbstractUser allows adding custom fields without rewriting the entire user model. It is used when
    the project requires storing additional information about users beyond the default fields"""
    username = models.CharField(db_index=True, max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(db_index=True, unique=True)
    avatar = models.ImageField(null=True, blank=True)
    bio = models.TextField(blank=True)
    posts_liked = models.ManyToManyField("core_posts.Post", related_name="liked_by")
    comments_liked = models.ManyToManyField(
        "core_comments.Comment", related_name="liked_by"
    )
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"  # this means the email field will be used as the "unique identifier" of this custom user model as opposed to the default username field.
    REQUIRED_FIELDS = [
        "username"
    ]  # list of the field names that will be prompted for when creating a user via the createsuperuser management command.

    objects = UserManager()

    def like_post(self, post):
        """Like `post` if it hasn't been done yet"""
        return self.posts_liked.add(post)

    def remove_liked_post(self, post):
        """Remove a like from a `post`"""
        return self.posts_liked.remove(post)

    def has_liked_post(self, post):
        """Return True if the user has liked a `post`;
        else False"""
        return self.posts_liked.filter(pk=post.pk).exists()

    def like_comment(self, comment):
        """Like `comment` if it hasn't been done yet"""
        return self.comments_liked.add(comment)

    def remove_liked_comment(self, comment):
        """Remove a like from a `comment`"""
        return self.comments_liked.remove(comment)

    def has_liked_comment(self, comment):
        """Return True if the user has liked a `comment`;
        else False"""
        return self.comments_liked.filter(pk=comment.pk).exists()

    def __str__(self):
        return f"{self.email}"

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"
