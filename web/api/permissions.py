from rest_framework.permissions import BasePermission
from rest_framework_api_key.permissions import HasAPIKey


class HasAPIKeyOrIsAuthenticated(BasePermission):
    """
    Permission class that allows access with either:
    1. Valid API Key authenticated by DRF
    2. Regular Django session authentication
    """

    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            return True

        return HasAPIKey().has_permission(request, view)
