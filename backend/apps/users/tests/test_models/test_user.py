"""
Tests for User model.
"""

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from apps.users.enums import UserRole, UserStatus
from apps.users.factories import UserFactory, AdminUserFactory, InactiveUserFactory

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    """Test suite for User model."""

    def test_create_user_with_factory(self):
        """Test creating a user with factory."""
        # Arrange & Act
        user = UserFactory()

        # Assert
        assert user.id is not None
        assert user.email is not None
        assert user.first_name is not None
        assert user.last_name is not None
        assert user.role == UserRole.USER
        assert user.status == UserStatus.ACTIVE
        assert user.is_active is True

    def test_user_string_representation(self):
        """Test User __str__ method."""
        # Arrange
        user = UserFactory(
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com'
        )

        # Act
        result = str(user)

        # Assert
        assert result == 'John Doe (john.doe@example.com)'

    def test_get_full_name(self):
        """Test get_full_name method."""
        # Arrange
        user = UserFactory(first_name='Jane', last_name='Smith')

        # Act
        full_name = user.get_full_name()

        # Assert
        assert full_name == 'Jane Smith'

    def test_get_full_name_returns_email_when_no_name(self):
        """Test get_full_name returns email when names are empty."""
        # Arrange
        user = UserFactory(first_name='', last_name='', email='test@example.com')

        # Act
        full_name = user.get_full_name()

        # Assert
        assert full_name == 'test@example.com'

    def test_get_short_name(self):
        """Test get_short_name method."""
        # Arrange
        user = UserFactory(first_name='Bob', last_name='Johnson')

        # Act
        short_name = user.get_short_name()

        # Assert
        assert short_name == 'Bob'

    def test_get_short_name_returns_email_when_no_first_name(self):
        """Test get_short_name returns email when first_name is empty."""
        # Arrange
        user = UserFactory(first_name='', email='test@example.com')

        # Act
        short_name = user.get_short_name()

        # Assert
        assert short_name == 'test@example.com'

    def test_is_admin_property_for_admin_user(self):
        """Test is_admin property returns True for admin users."""
        # Arrange
        admin = AdminUserFactory()

        # Act & Assert
        assert admin.is_admin is True

    def test_is_admin_property_for_regular_user(self):
        """Test is_admin property returns False for regular users."""
        # Arrange
        user = UserFactory(role=UserRole.USER)

        # Act & Assert
        assert user.is_admin is False

    def test_is_manager_property_for_manager_user(self):
        """Test is_manager property returns True for manager users."""
        # Arrange
        from apps.users.factories import ManagerUserFactory
        manager = ManagerUserFactory()

        # Act & Assert
        assert manager.is_manager is True

    def test_is_manager_property_for_regular_user(self):
        """Test is_manager property returns False for regular users."""
        # Arrange
        user = UserFactory(role=UserRole.USER)

        # Act & Assert
        assert user.is_manager is False

    def test_email_normalization_on_clean(self):
        """Test that email is normalized when clean() is called."""
        # Arrange
        user = UserFactory.build(email='TEST@EXAMPLE.COM')

        # Act
        user.clean()

        # Assert
        assert user.email == 'TEST@example.com'

    def test_email_uniqueness(self):
        """Test that email must be unique."""
        # Arrange
        email = 'unique@example.com'
        user1 = UserFactory(email=email)

        # Act & Assert
        # Factory uses get_or_create, so create directly to test constraint
        from django.db import IntegrityError
        with pytest.raises(IntegrityError):
            User.objects.create_user(
                email=email,
                password='testpass123',
                first_name='Test',
                last_name='User'
            )

    def test_phone_number_validation_valid(self):
        """Test phone number with valid format."""
        # Arrange & Act
        user = UserFactory(phone_number='+12345678901')

        # Assert
        assert user.phone_number == '+12345678901'

    def test_user_password_is_hashed(self):
        """Test that user password is properly hashed."""
        # Arrange
        user = UserFactory()

        # Act & Assert
        assert user.password != 'testpass123'
        assert user.check_password('testpass123') is True

    def test_inactive_user_status(self):
        """Test creating an inactive user."""
        # Arrange & Act
        user = InactiveUserFactory()

        # Assert
        assert user.status == UserStatus.INACTIVE
        assert user.is_active is False

    def test_user_default_ordering(self):
        """Test users are ordered by created_at descending."""
        # Arrange
        user1 = UserFactory()
        user2 = UserFactory()
        user3 = UserFactory()

        # Act
        users = User.objects.all()

        # Assert
        assert list(users) == [user3, user2, user1]

    def test_user_meta_db_table(self):
        """Test User model uses correct database table."""
        # Act & Assert
        assert User._meta.db_table == 'users'

    def test_username_field_is_email(self):
        """Test that USERNAME_FIELD is set to email."""
        # Act & Assert
        assert User.USERNAME_FIELD == 'email'

    def test_required_fields(self):
        """Test REQUIRED_FIELDS contains expected fields."""
        # Act & Assert
        assert 'first_name' in User.REQUIRED_FIELDS
        assert 'last_name' in User.REQUIRED_FIELDS
