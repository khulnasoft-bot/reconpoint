import importlib
import os
import tempfile
from unittest.mock import patch

from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase

import reconPoint.settings as settings_module


class SettingsImportTestCase(TestCase):
    """Tests for reconPoint settings import-time validation."""

    def tearDown(self) -> None:
        importlib.reload(settings_module)
        return super().tearDown()

    def test_production_requires_allowed_hosts(self):
        with tempfile.TemporaryDirectory() as temp_home:
            env = {
                "UI_DEBUG": "false",
                "ALLOWED_HOSTS": "",
                "DOMAIN_NAME": "example.com",
                "POSTGRES_DB": "testdb",
                "POSTGRES_USER": "testuser",
                "POSTGRES_PASSWORD": "testpass",
                "POSTGRES_HOST": "localhost",
                "POSTGRES_PORT": "5432",
                "RECONPOINT_HOME": temp_home,
            }
            with patch.dict(os.environ, env, clear=False):
                with patch("reconPoint.init.first_run", lambda secret_file, base_dir: "dummysecret"):
                    with self.assertRaises(ImproperlyConfigured):
                        importlib.reload(settings_module)

    def test_production_requires_websocket_allowed_origins(self):
        with tempfile.TemporaryDirectory() as temp_home:
            env = {
                "UI_DEBUG": "false",
                "ALLOWED_HOSTS": "example.com",
                "WEBSOCKET_ALLOWED_ORIGINS": "",
                "POSTGRES_DB": "testdb",
                "POSTGRES_USER": "testuser",
                "POSTGRES_PASSWORD": "testpass",
                "POSTGRES_HOST": "localhost",
                "POSTGRES_PORT": "5432",
                "RECONPOINT_HOME": temp_home,
            }
            with patch.dict(os.environ, env, clear=False):
                with patch("reconPoint.init.first_run", lambda secret_file, base_dir: "dummysecret"):
                    with self.assertRaises(ImproperlyConfigured):
                        importlib.reload(settings_module)

    def test_csrf_trusted_origins_defaults_from_domain_name(self):
        with tempfile.TemporaryDirectory() as temp_home:
            env = {
                "UI_DEBUG": "true",
                "ALLOWED_HOSTS": "localhost",
                "DOMAIN_NAME": "example.com",
                "CSRF_TRUSTED_ORIGINS": "",
                "POSTGRES_DB": "testdb",
                "POSTGRES_USER": "testuser",
                "POSTGRES_PASSWORD": "testpass",
                "POSTGRES_HOST": "localhost",
                "POSTGRES_PORT": "5432",
                "RECONPOINT_HOME": temp_home,
            }
            with patch.dict(os.environ, env, clear=False):
                with patch("reconPoint.init.first_run", lambda secret_file, base_dir: "dummysecret"):
                    settings = importlib.reload(settings_module)
        self.assertIn("https://example.com", settings.CSRF_TRUSTED_ORIGINS)
        self.assertIn("http://example.com", settings.CSRF_TRUSTED_ORIGINS)

    def test_debug_websocket_allowed_origins_defaults_local(self):
        with tempfile.TemporaryDirectory() as temp_home:
            env = {
                "UI_DEBUG": "true",
                "ALLOWED_HOSTS": "localhost",
                "POSTGRES_DB": "testdb",
                "POSTGRES_USER": "testuser",
                "POSTGRES_PASSWORD": "testpass",
                "POSTGRES_HOST": "localhost",
                "POSTGRES_PORT": "5432",
                "RECONPOINT_HOME": temp_home,
            }
            with patch.dict(os.environ, env, clear=False):
                with patch("reconPoint.init.first_run", lambda secret_file, base_dir: "dummysecret"):
                    settings = importlib.reload(settings_module)
        self.assertIn("http://localhost:8000", settings.WEBSOCKET_ALLOWED_ORIGINS)
        self.assertIn("http://127.0.0.1:8000", settings.WEBSOCKET_ALLOWED_ORIGINS)

    def test_production_uses_secure_settings(self):
        with tempfile.TemporaryDirectory() as temp_home:
            env = {
                "UI_DEBUG": "false",
                "ALLOWED_HOSTS": "example.com",
                "DOMAIN_NAME": "example.com",
                "POSTGRES_DB": "testdb",
                "POSTGRES_USER": "testuser",
                "POSTGRES_PASSWORD": "testpass",
                "POSTGRES_HOST": "localhost",
                "POSTGRES_PORT": "5432",
                "RECONPOINT_HOME": temp_home,
            }
            with patch.dict(os.environ, env, clear=False):
                with patch("reconPoint.init.first_run", lambda secret_file, base_dir: "dummysecret"):
                    settings = importlib.reload(settings_module)
        self.assertTrue(settings.SECURE_SSL_REDIRECT)
        self.assertEqual(settings.SECURE_HSTS_SECONDS, 63072000)
        self.assertTrue(settings.SECURE_HSTS_INCLUDE_SUBDOMAINS)
        self.assertTrue(settings.SECURE_HSTS_PRELOAD)
        self.assertTrue(settings.SESSION_COOKIE_SECURE)
        self.assertTrue(settings.CSRF_COOKIE_SECURE)
        self.assertEqual(settings.X_FRAME_OPTIONS, "DENY")
