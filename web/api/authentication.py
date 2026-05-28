from __future__ import annotations

from django.conf import settings
from django.utils import timezone
from rest_framework import authentication, exceptions
from rest_framework_api_key.models import APIKey

from dashboard.models import UserAPIKey


class APIKeyAuthentication(authentication.BaseAuthentication):
    """Authenticate DRF requests using a configured API key header."""

    def authenticate(self, request):
        auth_header = (request.META.get("HTTP_AUTHORIZATION", "") or "").strip()
        if not auth_header:
            return None

        for header_name in self._get_configured_header_names():
            prefix = f"{header_name} "
            if auth_header.lower().startswith(prefix.lower()):
                key = auth_header[len(prefix) :].strip()
                if not key:
                    raise exceptions.AuthenticationFailed("Invalid API key header.")
                return self.authenticate_credentials(key)

        return None

    def authenticate_credentials(self, key):
        try:
            api_key = UserAPIKey.objects.get_from_key(key)
        except (UserAPIKey.DoesNotExist, APIKey.DoesNotExist):
            raise exceptions.AuthenticationFailed("Invalid API key.")

        if not api_key.is_active:
            raise exceptions.AuthenticationFailed("API key inactive.")

        if api_key.expiry_date and api_key.expiry_date <= timezone.now():
            raise exceptions.AuthenticationFailed("API key expired.")

        user = api_key.user
        if not user or not user.is_active:
            raise exceptions.AuthenticationFailed("API key owner account is disabled.")

        return user, api_key

    def authenticate_header(self, request):
        return self._get_configured_header_names()[0]

    def _get_configured_header_names(self) -> list[str]:
        configured_header_name = (getattr(settings, "SECATOR_ADDONS_API_HEADER_NAME", "") or "Api-Key").strip()
        candidate_header_names = [configured_header_name, "Api-Key"]
        return list(dict.fromkeys([name for name in candidate_header_names if name]))
