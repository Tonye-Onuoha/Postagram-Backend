from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError as DjangoValidationError
from core.comments.models import Comment
from core.posts.models import Post
from core.users.models import User
from core.comments.serializers import CommentSerializer
from core.auth.permissions import UserPermission

# Create your views here.
@api_view(["GET", "POST"])
@permission_classes([UserPermission])
def get_or_create_comments(request, post_pk):
    if request.method == "GET":
        if request.user.is_superuser:
            comments = Comment.objects.all().order_by('-updated')
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            try:
                post = Post.objects.get_object_by_public_id(post_pk)
            except Post.DoesNotExist:
                raise ValidationError(f'There is no post with public id "{post_pk}"')
            else:
                post_comments = Comment.objects.filter(post__public_id=post.public_id).order_by('-updated')
                serializer = CommentSerializer(post_comments, many=True, context={'request':request})
                return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == "POST":
        serializer = CommentSerializer(data=request.data, context={'request':request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET", "PUT", "DELETE"])
@permission_classes([UserPermission])
def comment_id(request, post_pk, comment_pk):
    try:
        comment = Comment.objects.get_object_by_public_id(comment_pk)
        post = Post.objects.get_object_by_public_id(post_pk)
    except DjangoValidationError:
        raise ValidationError(f'You entered an invalid UUID' )
    except Comment.DoesNotExist:
        raise ValidationError(f'There is no comment with public id "{comment_pk}"')
    except Post.DoesNotExist:
        raise ValidationError(f'There is no post with public id "{post_pk}"')

    if request.method == "GET":
        serializer = CommentSerializer(comment, context={'request':request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == "PUT":
        # check object permissions
        permission = UserPermission()
        permission.has_object_permission(request, comment) # raises an exception if object permission-check fails
        serializer = CommentSerializer(comment, data=request.data, context={'request':request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    if request.method == "DELETE":
        if (request.user == post.author and request.user == comment.post.author) or request.user == comment.author or request.user.is_superuser:
            comment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def like_comment(request, post_pk,comment_pk):
    try:
        comment = Comment.objects.get_object_by_public_id(comment_pk)
        current_user = User.objects.get_object_by_public_id(request.user.public_id)
    except DjangoValidationError:
        raise ValidationError(f'{comment_pk} is not a valid UUID' )
    except Comment.DoesNotExist:
        raise ValidationError(f'There is no comment with public id "{comment_pk}"')
    except User.DoesNotExist:
        raise ValidationError(f'There is no user with public id "{request.user.public_id}"')
    else:
        # perform a like on this comment by the current user
        current_user.like_comment(comment)
        serializer = CommentSerializer(comment, context={'request':request})
        return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def unlike_comment(request, post_pk, comment_pk):
    try:
        comment = Comment.objects.get_object_by_public_id(comment_pk)
        current_user = User.objects.get_object_by_public_id(request.user.public_id)
    except DjangoValidationError:
        raise ValidationError(f'{comment_pk} is not a valid UUID' )
    except Comment.DoesNotExist:
        raise ValidationError(f'There is no comment with public id "{comment_pk}"')
    except User.DoesNotExist:
        raise ValidationError(f'There is no user with public id "{request.user.public_id}"')
    else:
        # remove a like on this comment by the current user
        current_user.remove_liked_comment(comment)
        serializer = CommentSerializer(comment, context={'request':request})
        return Response(serializer.data, status=status.HTTP_200_OK)



