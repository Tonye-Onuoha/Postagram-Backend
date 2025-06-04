from django.urls import path
from .views import get_users, get_user

urlpatterns = [
    path('', get_users, name='users'),
    path('<public_id>/', get_user, name='user-detail'),
]
