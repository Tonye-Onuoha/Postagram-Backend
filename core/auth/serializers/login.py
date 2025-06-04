from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.settings import api_settings
from core.users.serializers import UserSerializer
from typing import Any, Dict


class LoginSerializer(TokenObtainPairSerializer):
    # The "is_valid" method will call this method, passing the request.data as an argument to the "attrs" parameter.
    def validate(self, attrs):
        # We validate the data in the parent class.
        data = super().validate(attrs)
        # The "data" variable above now contains the refresh and access tokens obtained from the parent class.
        # The ".user" attribute becomes available to this serializer the moment the data is validated.
        # Below, we update the data to include the serialized user object.
        data["user"] = UserSerializer(self.user, context=self.context).data

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)
        # The data is then returned and stored as the value of the ".validated_data" attribute of the serializer.
        return data
