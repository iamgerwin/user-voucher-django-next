"""
Tests for UserCreateSerializer.
"""

import pytest
from django.contrib.auth import get_user_model

from apps.users.serializers import UserCreateSerializer
from apps.users.enums import UserRole, UserStatus

User = get_user_model()


@pytest.mark.django_db
class TestUserCreateSerializer:
    """Test suite for UserCreateSerializer."""

    def test_create_user_with_valid_data(self):
        """Test creating a user with valid data."""
        # Arrange
        data = {
            'email': 'newuser@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
            'first_name': 'New',
            'last_name': 'User',
        }

        # Act
        serializer = UserCreateSerializer(data=data)

        # Assert
        assert serializer.is_valid()
        user = serializer.save()
        assert user.email == 'newuser@example.com'
        assert user.first_name == 'New'
        assert user.last_name == 'User'
        assert user.check_password('SecurePass123!') is True

    def test_password_is_not_in_output(self):
        """Test password field is write-only and not in output."""
        # Arrange
        data = {
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
            'first_name': 'Test',
            'last_name': 'User',
        }

        # Act
        serializer = UserCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        output_serializer = UserCreateSerializer(user)

        # Assert
        assert 'password' not in output_serializer.data
        assert 'password_confirm' not in output_serializer.data

    def test_password_mismatch_validation(self):
        """Test validation fails when passwords don't match."""
        # Arrange
        data = {
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'DifferentPass123!',
            'first_name': 'Test',
            'last_name': 'User',
        }

        # Act
        serializer = UserCreateSerializer(data=data)

        # Assert
        assert not serializer.is_valid()
        assert 'password_confirm' in serializer.errors

    def test_weak_password_validation(self):
        """Test validation fails with weak password."""
        # Arrange
        data = {
            'email': 'test@example.com',
            'password': '123',
            'password_confirm': '123',
            'first_name': 'Test',
            'last_name': 'User',
        }

        # Act
        serializer = UserCreateSerializer(data=data)

        # Assert
        assert not serializer.is_valid()
        assert 'password' in serializer.errors

    def test_missing_required_fields(self):
        """Test validation fails when required fields are missing."""
        # Arrange
        data = {
            'email': 'test@example.com',
        }

        # Act
        serializer = UserCreateSerializer(data=data)

        # Assert
        assert not serializer.is_valid()
        assert 'password' in serializer.errors
        assert 'password_confirm' in serializer.errors
        assert 'first_name' in serializer.errors
        assert 'last_name' in serializer.errors

    def test_invalid_email_format(self):
        """Test validation fails with invalid email format."""
        # Arrange
        data = {
            'email': 'notanemail',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
            'first_name': 'Test',
            'last_name': 'User',
        }

        # Act
        serializer = UserCreateSerializer(data=data)

        # Assert
        assert not serializer.is_valid()
        assert 'email' in serializer.errors

    def test_duplicate_email(self):
        """Test validation fails when email already exists."""
        # Arrange
        from apps.users.factories import UserFactory
        from django.db import IntegrityError
        existing_user = UserFactory(email='existing@example.com')

        data = {
            'email': 'existing@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
            'first_name': 'Test',
            'last_name': 'User',
        }

        # Act
        serializer = UserCreateSerializer(data=data)

        # Assert
        # ModelSerializer includes UniqueValidator for email field
        assert not serializer.is_valid()
        assert 'email' in serializer.errors

    def test_create_user_with_phone_number(self):
        """Test creating user with optional phone number."""
        # Arrange
        data = {
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
            'first_name': 'Test',
            'last_name': 'User',
            'phone_number': '+12345678901',
        }

        # Act
        serializer = UserCreateSerializer(data=data)

        # Assert
        assert serializer.is_valid()
        user = serializer.save()
        assert user.phone_number == '+12345678901'

    def test_password_is_hashed(self):
        """Test password is properly hashed when creating user."""
        # Arrange
        password = 'SecurePass123!'
        data = {
            'email': 'test@example.com',
            'password': password,
            'password_confirm': password,
            'first_name': 'Test',
            'last_name': 'User',
        }

        # Act
        serializer = UserCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Assert
        assert user.password != password
        assert user.check_password(password) is True

    def test_password_confirm_removed_from_validated_data(self):
        """Test password_confirm is removed before creating user."""
        # Arrange
        data = {
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
            'first_name': 'Test',
            'last_name': 'User',
        }

        # Act
        serializer = UserCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        # Assert
        assert 'password_confirm' not in validated_data
        assert 'password' in validated_data
