from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from core.users.models import User
from core.users.serializers import UserSerializer
from core.auth.serializers.register import RegisterSerializer
from core.auth.serializers.login import LoginSerializer


# Create your views here.
@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    if request.method == "POST":
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user_serializer = UserSerializer(user, context={'request':request})
        refresh = RefreshToken.for_user(user)
        res = {"access": str(refresh.access_token), "refresh": str(refresh)}
        return Response({"user": user_serializer.data, "access": res["access"], "refresh": res["refresh"]}, status=status.HTTP_201_CREATED)

@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    if request.method == "POST":
        serializer = LoginSerializer(data=request.data, context={'request':request})
        if serializer.is_valid():
            # the validated data will contain the refresh and access tokens.
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    if request.method == "POST":
        refresh_token = request.data.get("refresh")
        if refresh_token is None:
            raise ValidationError({"detail":"A refresh token is required."})
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except TokenError:
            # return the following as a HTTP response. "ValidationError" will return 400_BAD_REQUEST status-code by default.
            raise ValidationError({"detail":"The refresh token is invalid."})

