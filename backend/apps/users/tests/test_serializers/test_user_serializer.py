"""
Tests for UserSerializer.
"""

import pytest
from django.contrib.auth import get_user_model

from apps.users.serializers import UserSerializer, UserListSerializer, UserAdminSerializer
from apps.users.factories import UserFactory, AdminUserFactory

User = get_user_model()


@pytest.mark.django_db
class TestUserSerializer:
    """Test suite for UserSerializer."""

    def test_serialize_user(self):
        """Test serializing a user."""
        # Arrange
        user = UserFactory(
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )

        # Act
        serializer = UserSerializer(user)
        data = serializer.data

        # Assert
        assert data['id'] == user.id
        assert data['email'] == 'test@example.com'
        assert data['first_name'] == 'Test'
        assert data['last_name'] == 'User'
        assert data['full_name'] == 'Test User'
        assert 'password' not in data

    def test_serialize_user_full_name(self):
        """Test full_name field is correctly generated."""
        # Arrange
        user = UserFactory(first_name='John', last_name='Doe')

        # Act
        serializer = UserSerializer(user)

        # Assert
        assert serializer.data['full_name'] == 'John Doe'

    def test_serializer_read_only_fields(self):
        """Test read-only fields cannot be updated."""
        # Arrange
        user = UserFactory()
        original_created_at = user.created_at

        # Act
        serializer = UserSerializer(
            user,
            data={'created_at': '2020-01-01T00:00:00Z'},
            partial=True
        )

        # Assert
        assert serializer.is_valid()
        serializer.save()
        user.refresh_from_db()
        assert user.created_at == original_created_at

    def test_validate_email_uniqueness_on_update(self):
        """Test email validation prevents duplicate emails on update."""
        # Arrange
        user1 = UserFactory(email='user1@example.com')
        user2 = UserFactory(email='user2@example.com')

        # Act
        serializer = UserSerializer(
            user2,
            data={'email': 'user1@example.com'},
            partial=True
        )

        # Assert
        assert not serializer.is_valid()
        assert 'email' in serializer.errors

    def test_validate_email_same_email_on_update(self):
        """Test user can keep their own email on update."""
        # Arrange
        user = UserFactory(email='user@example.com')

        # Act
        serializer = UserSerializer(
            user,
            data={'email': 'user@example.com', 'first_name': 'Updated'},
            partial=True
        )

        # Assert
        assert serializer.is_valid()

    def test_serializer_excludes_sensitive_fields(self):
        """Test serializer excludes password and other sensitive fields."""
        # Arrange
        user = UserFactory()

        # Act
        serializer = UserSerializer(user)
        data = serializer.data

        # Assert
        assert 'password' not in data
        assert 'is_superuser' not in data


@pytest.mark.django_db
class TestUserListSerializer:
    """Test suite for UserListSerializer."""

    def test_serialize_user_list(self):
        """Test serializing users with minimal fields."""
        # Arrange
        user = UserFactory()

        # Act
        serializer = UserListSerializer(user)
        data = serializer.data

        # Assert
        assert 'id' in data
        assert 'email' in data
        assert 'full_name' in data
        assert 'role' in data
        assert 'status' in data
        assert 'date_joined' in data
        # Should not include detailed fields
        assert 'phone_number' not in data
        assert 'is_active' not in data

    def test_all_fields_are_read_only(self):
        """Test all fields in list serializer are read-only."""
        # Arrange
        user = UserFactory()

        # Act
        serializer = UserListSerializer(user)

        # Assert
        assert serializer.Meta.read_only_fields == serializer.Meta.fields


@pytest.mark.django_db
class TestUserAdminSerializer:
    """Test suite for UserAdminSerializer."""

    def test_serialize_admin_user_with_counts(self):
        """Test admin serializer includes voucher counts."""
        # Arrange
        user = AdminUserFactory()

        # Act
        serializer = UserAdminSerializer(user)
        data = serializer.data

        # Assert
        assert 'voucher_count' in data
        assert 'voucher_usage_count' in data
        assert 'is_staff' in data
        assert 'is_superuser' in data

    def test_voucher_count_field(self):
        """Test voucher_count field shows correct count."""
        # Arrange
        user = UserFactory()
        # Create vouchers for the user
        from apps.vouchers.factories import PercentageDiscountVoucherFactory
        PercentageDiscountVoucherFactory(created_by=user)
        PercentageDiscountVoucherFactory(created_by=user)

        # Act
        serializer = UserAdminSerializer(user)

        # Assert
        assert serializer.data['voucher_count'] == 2

    def test_voucher_usage_count_field(self):
        """Test voucher_usage_count field shows correct count."""
        # Arrange
        user = UserFactory()
        # Create voucher usages for the user
        from apps.vouchers.factories import VoucherUsageFactory
        VoucherUsageFactory(user=user)
        VoucherUsageFactory(user=user)
        VoucherUsageFactory(user=user)

        # Act
        serializer = UserAdminSerializer(user)

        # Assert
        assert serializer.data['voucher_usage_count'] == 3
