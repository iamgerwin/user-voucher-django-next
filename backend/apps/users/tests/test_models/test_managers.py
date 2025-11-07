"""
Tests for User managers.
"""

import pytest
from django.contrib.auth import get_user_model

from apps.users.enums import UserRole, UserStatus

User = get_user_model()


@pytest.mark.django_db
class TestUserManager:
    """Test suite for UserManager."""

    def test_create_user_with_email_and_password(self):
        """Test creating a user with email and password."""
        # Arrange
        email = 'newuser@example.com'
        password = 'securepass123'

        # Act
        user = User.objects.create_user(
            email=email,
            password=password,
            first_name='New',
            last_name='User'
        )

        # Assert
        assert user.email == email
        assert user.check_password(password) is True
        assert user.role == UserRole.USER
        assert user.status == UserStatus.ACTIVE
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False

    def test_create_user_without_email_raises_error(self):
        """Test that creating a user without email raises ValueError."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match='The Email field must be set'):
            User.objects.create_user(email='', password='pass123')

    def test_create_user_with_none_email_raises_error(self):
        """Test that creating a user with None email raises ValueError."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match='The Email field must be set'):
            User.objects.create_user(email=None, password='pass123')

    def test_create_user_normalizes_email(self):
        """Test that email is normalized when creating user."""
        # Arrange
        email = 'User@EXAMPLE.COM'

        # Act
        user = User.objects.create_user(
            email=email,
            password='pass123',
            first_name='Test',
            last_name='User'
        )

        # Assert
        assert user.email == 'User@example.com'

    def test_create_user_with_custom_role(self):
        """Test creating a user with custom role."""
        # Arrange & Act
        user = User.objects.create_user(
            email='manager@example.com',
            password='pass123',
            role=UserRole.MANAGER,
            first_name='Manager',
            last_name='User'
        )

        # Assert
        assert user.role == UserRole.MANAGER

    def test_create_superuser(self):
        """Test creating a superuser."""
        # Arrange
        email = 'admin@example.com'
        password = 'adminpass123'

        # Act
        user = User.objects.create_superuser(
            email=email,
            password=password,
            first_name='Admin',
            last_name='User'
        )

        # Assert
        assert user.email == email
        assert user.check_password(password) is True
        assert user.role == UserRole.ADMIN
        assert user.status == UserStatus.ACTIVE
        assert user.is_staff is True
        assert user.is_superuser is True
        assert user.is_active is True

    def test_create_superuser_with_is_staff_false_raises_error(self):
        """Test that creating superuser with is_staff=False raises ValueError."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match='Superuser must have is_staff=True'):
            User.objects.create_superuser(
                email='admin@example.com',
                password='pass123',
                is_staff=False,
                first_name='Admin',
                last_name='User'
            )

    def test_create_superuser_with_is_superuser_false_raises_error(self):
        """Test that creating superuser with is_superuser=False raises ValueError."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match='Superuser must have is_superuser=True'):
            User.objects.create_superuser(
                email='admin@example.com',
                password='pass123',
                is_superuser=False,
                first_name='Admin',
                last_name='User'
            )

    def test_create_user_without_password(self):
        """Test creating a user without password sets unusable password."""
        # Arrange & Act
        user = User.objects.create_user(
            email='nopass@example.com',
            first_name='No',
            last_name='Password'
        )

        # Assert
        assert user.has_usable_password() is False

    def test_create_multiple_users(self):
        """Test creating multiple users."""
        # Arrange & Act
        user1 = User.objects.create_user(
            email='user1@example.com',
            password='pass123',
            first_name='User',
            last_name='One'
        )
        user2 = User.objects.create_user(
            email='user2@example.com',
            password='pass123',
            first_name='User',
            last_name='Two'
        )

        # Assert
        assert User.objects.count() == 2
        assert user1.email != user2.email
