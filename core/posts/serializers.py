from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from core.abstract.serializers import AbstractSerializer
from core.posts.models import Post
from core.users.models import User
from core.users.serializers import UserSerializer

class PostSerializer(AbstractSerializer):
    author = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field='public_id')
    # The Serializer class in Django provides ways to create the write_only values that will be sent on the response.
    liked = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    # In the preceding code, we are using the serializers.SerializerMethodField() field, which allows us to write a custom function that will return a value we want to attribute to this field.
    # The syntax of the method will be get_field, where field is the name of the field declared on the serializer.
    # That is why for liked, we have the get_liked method, and for likes_count, we have the get_likes_count method.

    def get_liked(self, instance):
        request = self.context.get('request', None)
        if request is None or request.user.is_anonymous:
            return False
        return request.user.has_liked_post(instance)

    def get_likes_count(self, instance):
        return instance.liked_by.count()

    def get_comments_count(self, instance):
        return instance.comment_set.all().count()

    def update(self, instance, validated_data):
        # We update the validated data first to set edited as "True" before calling the base class which then marks the instance edited attribute as "True".
        if not instance.edited:
            validated_data['edited'] = True
        instance = super().update(instance, validated_data)
        return instance

    def validate_author(self, value):
        # A context dictionary can be passed in every serializer. It usually contains the request object that we can use to make some checks.
        if self.context["request"].user != value:
            raise ValidationError("You can't create a post for another user.")
        return value

    def to_representation(self, instance):
        """
        Object instance -> Dict of primitive datatypes. This method is usually triggered when we access the '.data' property
        """
        # The to_representation() method takes the object instance that requires serialization and returns a primitive representation.
        # This usually means returning a structure of built-in Python data types.
        # We update the representation of the serialized post to represent the author field as a serialized user rather than a public id.
        representation = super().to_representation(instance)
        author = User.objects.get_object_by_public_id(representation["author"])
        representation["author"] = UserSerializer(author, context=self.context).data
        return representation

    class Meta:
        model = Post
        # List of all the fields that can be included in a
        # request or a response
        fields = ['id', 'author', 'body', 'edited', 'liked', 'likes_count', 'comments_count', 'created', 'updated']
        read_only_fields = ["edited"]
