from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import LimitOffsetPagination
from django.core.exceptions import ValidationError as DjangoValidationError
from core.auth.permissions import UserPermission
from core.users.models import User
from core.users.serializers import UserSerializer


# Create your views here.
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_users(request):
    if request.method == "GET":
        users = User.objects.all().order_by('-updated')
        if bool(request.query_params.get("limit", None)):
            paginator = LimitOffsetPagination()
            results = paginator.paginate_queryset(users, request)
            serializer = UserSerializer(results, many=True, context={'request':request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            serializer = UserSerializer(users, many=True, context={'request':request})
            return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(["GET", "PATCH"])
@permission_classes([UserPermission])
def get_user(request, public_id):
    try:
        user = User.objects.get_object_by_public_id(public_id)
    except DjangoValidationError:
        raise ValidationError(f'{public_id} is not a valid UUID' )
    except User.DoesNotExist:
        raise ValidationError("There is no user with this public id!")

    if request.method == "GET":
        if not request.user.is_anonymous:
            serializer = UserSerializer(user, context={'request':request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    elif request.method == "PATCH":
        # check object permissions
        permission = UserPermission()
        permission.has_object_permission(request, user) # raises an exception if object permission-check fails
        serializer = UserSerializer(user, data=request.data, partial=True, context={'request':request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
