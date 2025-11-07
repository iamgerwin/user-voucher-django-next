"""
Global pytest fixtures for the entire test suite.
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    """
    Fixture for DRF API client.
    """
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, user):
    """
    Fixture for authenticated API client with regular user.
    """
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    """
    Fixture for authenticated API client with admin user.
    """
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def user(db):
    """
    Fixture for a regular user.
    Uses factory if available, otherwise creates manually.
    """
    try:
        from apps.users.factories import UserFactory
        return UserFactory()
    except ImportError:
        from apps.users.enums import UserRole, UserStatus
        return User.objects.create_user(
            email='user@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role=UserRole.USER,
            status=UserStatus.ACTIVE
        )


@pytest.fixture
def admin_user(db):
    """
    Fixture for an admin user.
    Uses factory if available, otherwise creates manually.
    """
    try:
        from apps.users.factories import UserFactory
        from apps.users.enums import UserRole
        return UserFactory(role=UserRole.ADMIN, is_staff=True, is_superuser=True)
    except ImportError:
        from apps.users.enums import UserRole, UserStatus
        return User.objects.create_superuser(
            email='admin@example.com',
            password='testpass123',
            first_name='Admin',
            last_name='User',
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )


@pytest.fixture
def manager_user(db):
    """
    Fixture for a manager user.
    """
    try:
        from apps.users.factories import UserFactory
        from apps.users.enums import UserRole
        return UserFactory(role=UserRole.MANAGER)
    except ImportError:
        from apps.users.enums import UserRole, UserStatus
        return User.objects.create_user(
            email='manager@example.com',
            password='testpass123',
            first_name='Manager',
            last_name='User',
            role=UserRole.MANAGER,
            status=UserStatus.ACTIVE
        )
