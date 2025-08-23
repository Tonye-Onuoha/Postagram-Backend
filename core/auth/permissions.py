from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.exceptions import PermissionDenied
from core.users.models import User


class UserPermission(BasePermission):
    def has_permission(self, request, view):
        """This method gets called automatically when this permission is used in a function-based view"""
        if request.method == "GET" or request.method == "POST":
            if request.user.is_anonymous:
                return request.method in SAFE_METHODS
            return bool(request.user and request.user.is_authenticated)
        elif (
            request.method == "PUT"
            or request.method == "PATCH"
            or request.method == "DELETE"
        ):
            return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, obj):
        if isinstance(obj, User):
            if request.user.is_superuser or request.user == obj:
                return
            else:
                raise PermissionDenied
        else:
            if request.user.is_superuser:
                return
            elif request.user != obj.author:
                raise PermissionDenied

    # Permission doesn't determine authentication. Authentication is determined when the authorization header is passed with valid credentials.
    # If the user is authenticated (i.e not anonymous) but the permission returns False, then you get a 403 (Forbidden) status code.
    # If the user is anonymous but the permission returns False, then it falls back to a 401 (Unauthorized) status code.
    # Use view.http_method_names to see the request methods that the view accepts.
    # SAFE_METHODS (typically GET AND HEAD) are methods that ensure that no action will occur on the server as a result of the HTTP request.
    # By action, we mean that the server will perform an operation on behalf of the client e.g credit card being charged for a purchase.
