from rest_framework import serializers
from core.users.models import User
from core.abstract.serializers import AbstractSerializer
from django.conf import settings

class UserSerializer(AbstractSerializer):

    posts_count = serializers.SerializerMethodField()

    def get_posts_count(self, instance):
        """Return the number of posts a user has created."""
        return instance.post_set.all().count()

    def to_representation(self, instance):
        """
        Object instance -> Dict of primitive datatypes. This method is usually triggered when we access the '.data' property.
        """
        # The to_representation() method takes the object instance that requires serialization and returns a primitive representation.
        # This usually means returning a structure of built-in Python data types.
        representation = super().to_representation(instance)
        if not bool(representation["avatar"]):
            representation["avatar"] = settings.DEFAULT_AVATAR_URL
        if settings.DEBUG: # debug enabled for dev
            request = self.context.get('request')
            representation['avatar'] = request.build_absolute_uri(representation['avatar'])
        return representation

        # By default, Django doesn’t return the actual route of the file with the domain. That’s why in this case, if we are in a
        # development environment, we return an absolute URL of the avatar using request.build_absolute_uri().

    class Meta:
        model = User
        fields = ['id', 'public_id', 'username', 'first_name', 'last_name', 'name', 'bio', 'avatar', 'email', 'is_active', 'created', 'updated', 'posts_count']
        read_only_field = ['is_active']
