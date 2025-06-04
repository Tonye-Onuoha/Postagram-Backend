from django.urls import path, include

urlpatterns = [
    path('core/users/', include('core.users.urls')),
    path('core/auth/', include('core.auth.urls')),
    path('core/posts/', include('core.posts.urls')),
]
