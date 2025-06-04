from django.urls import path
from .views import get_or_create_posts, post_id, like_post, unlike_post
from core.comments.views import get_or_create_comments, comment_id, like_comment, unlike_comment

urlpatterns = [
    path('', get_or_create_posts, name='posts'),
    path('<post_id>/', post_id, name='post-detail'),
    path('<post_pk>/like/', like_post, name='like-post'),
    path('<post_pk>/remove_like/', unlike_post, name='unlike-post'),
    path('<post_pk>/comment/', get_or_create_comments, name='list-or-create-comments'),
    path('<post_pk>/comment/<comment_pk>/', comment_id, name='get-or-update-or-delete-comment'),
    path('<post_pk>/comment/<comment_pk>/like/', like_comment, name='like-comment'),
    path('<post_pk>/comment/<comment_pk>/remove_like/', unlike_comment, name='unlike-comment'),
]
