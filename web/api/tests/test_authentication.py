from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, override_settings
from rest_framework.exceptions import AuthenticationFailed

from api.authentication import APIKeyAuthentication
from dashboard.models import UserAPIKey
from utils.test_base import BaseTestCase


class APIKeyAuthenticationTestCase(BaseTestCase):
    """Unit tests for the APIKeyAuthentication backend."""

    def setUp(self) -> None:
        super().setUp()
        self.factory = RequestFactory()
        self.authenticator = APIKeyAuthentication()

    def test_authenticate_with_valid_api_key_returns_user_and_api_key(self):
        api_key_obj, raw_key = UserAPIKey.objects.create_key(name="test-key", user=self.user, is_active=True)
        request = self.factory.get("/api/test/", HTTP_AUTHORIZATION=f"Api-Key {raw_key}")

        result = self.authenticator.authenticate(request)

        self.assertIsNotNone(result)
        user, auth = result
        self.assertEqual(user, self.user)
        self.assertEqual(auth, api_key_obj)

    def test_authenticate_header_returns_configured_header_name(self):
        self.assertEqual(self.authenticator.authenticate_header(self.factory.get("/api/test/")), "Api-Key")

    def test_authenticate_with_invalid_api_key_raises_authentication_failed(self):
        request = self.factory.get("/api/test/", HTTP_AUTHORIZATION="Api-Key invalid-key")

        with self.assertRaises(AuthenticationFailed):
            self.authenticator.authenticate(request)

    def test_authenticate_with_unrecognized_header_returns_none(self):
        request = self.factory.get("/api/test/", HTTP_AUTHORIZATION="Bearer token")

        self.assertIsNone(self.authenticator.authenticate(request))

    def test_authenticate_header_uses_configured_header_name(self):
        with override_settings(SECATOR_ADDONS_API_HEADER_NAME="X-Api-Key"):
            api_key_obj, raw_key = UserAPIKey.objects.create_key(name="test-key", user=self.user, is_active=True)
            request = self.factory.get("/api/test/", HTTP_AUTHORIZATION=f"X-Api-Key {raw_key}")

            result = self.authenticator.authenticate(request)

            self.assertIsNotNone(result)
            user, auth = result
            self.assertEqual(user, self.user)
            self.assertEqual(auth, api_key_obj)
