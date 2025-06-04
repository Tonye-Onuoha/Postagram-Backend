from rest_framework import serializers
from core.users.serializers import UserSerializer
from core.abstract.serializers import AbstractSerializer
from core.users.models import User
from core.posts.models import Post
class RegisterSerializer(AbstractSerializer):
    """
    Registration serializer for requests and user creation
    """
    # Making sure the password is at least 8 characterslong, and no longer than 128 and can't be read
    # by the user
    password = serializers.CharField(max_length=128,min_length=8, write_only=True, required=True)
    class Meta:
        model = User
        # List of all the fields that can be included in a request or a response
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'bio', 'password']

    def create(self, validated_data):
        # Use the `create_user` method we wrote earlier for the UserManager to create a new user.
        # This method would have still run automatically. We just made it explicit.
        return User.objects.create_user(**validated_data)
