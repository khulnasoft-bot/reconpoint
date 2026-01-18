import os
import django

# Configure Django settings before importing models
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reconPoint.settings')
django.setup()

# Pytest configuration fixtures
import pytest
from django.contrib.auth import get_user_model
from django.test.client import Client


User = get_user_model()


@pytest.fixture
def db(db):
    """Ensure database is available for all tests that need it."""
    return db


@pytest.fixture
def client():
    """Provide Django test client."""
    return Client()


@pytest.fixture
def user():
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        email='testuser@example.com',
        password='testpass123'
    )


@pytest.fixture
def admin_user():
    """Create a test admin user."""
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpass123'
    )


@pytest.fixture
def authenticated_client(client, user):
    """Provide an authenticated Django test client."""
    client.force_login(user)
    return client


@pytest.fixture
def admin_client(client, admin_user):
    """Provide an authenticated Django test client with admin privileges."""
    client.force_login(admin_user)
    return client
