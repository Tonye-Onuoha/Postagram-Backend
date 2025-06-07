from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError as DjangoValidationError
from core.auth.permissions import UserPermission
from .models import Post
from .serializers import PostSerializer
from core.users.models import User

# Create your views here.
@api_view(["GET", "POST"])
@permission_classes([UserPermission])
def get_or_create_posts(request):
    if request.method == "GET":
        # get posts by a specific user/author.
        if bool(request.query_params.get('author_public_id', None)):
            author_id = request.query_params.get('author_public_id')
            author_posts = Post.objects.filter(author__public_id=author_id)
            post = author_posts.first()
            if post:
                permission = UserPermission()
                permission.has_object_permission(request, post) # raises an exception if object permission-check fails
            serializer = PostSerializer(author_posts, many=True, context={'request':request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # get posts by all users.
            posts = Post.objects.all().order_by('-updated')
            serializer = PostSerializer(posts, many=True, context={'request':request})
            return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == "POST":
        serializer = PostSerializer(data=request.data, context={'request':request})
        # return response if serializer is valid, else raise an exception.
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(["GET", "PUT", "DELETE"])
@permission_classes([UserPermission])
def post_id(request, post_id):
    try:
        post = Post.objects.get_object_by_public_id(public_id=post_id)
    except DjangoValidationError:
        raise ValidationError(f'{post_id} is not a valid UUID' )
    except Post.DoesNotExist:
        raise ValidationError(f'There is no post with public id "{post_id}"')

    if request.method == "GET":
        serializer = PostSerializer(post, context={'request':request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == "PUT":
        serializer = PostSerializer(post, data=request.data, context={'request':request})
        # check object permissions
        permission = UserPermission()
        permission.has_object_permission(request, post) # raises an exception if object permission-check fails
        # return response if serializer is valid, else raise an exception
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == "DELETE":
        # check object permissions
        permission = UserPermission()
        permission.has_object_permission(request, post) # raises an exception if object permission-check fails
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def like_post(request, post_pk):
    try:
        post = Post.objects.get_object_by_public_id(post_pk)
        current_user = User.objects.get_object_by_public_id(request.user.public_id)
    except Post.DoesNotExist:
        raise ValidationError(f'There is no post with public id "{post_pk}"')
    except User.DoesNotExist:
        raise ValidationError(f'There is no user with public id "{request.user.public_id}"')
    else:
        # perform a like on this post by the current user
        current_user.like_post(post)
        serializer = PostSerializer(post, context={'request':request})
        return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def unlike_post(request, post_pk):
    try:
        post = Post.objects.get_object_by_public_id(post_pk)
        current_user = User.objects.get_object_by_public_id(request.user.public_id)
    except Post.DoesNotExist:
        raise ValidationError(f'There is no post with public id "{post_pk}"')
    except User.DoesNotExist:
        raise ValidationError(f'There is no user with public id "{request.user.public_id}"')
    else:
        # remove a like on this post by the current user
        current_user.remove_liked_post(post)
        serializer = PostSerializer(post, context={'request':request})
        return Response(serializer.data, status=status.HTTP_200_OK)


