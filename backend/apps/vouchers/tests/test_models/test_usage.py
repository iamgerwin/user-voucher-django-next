"""
Tests for VoucherUsage model.
"""

from decimal import Decimal

import pytest

from apps.vouchers.factories import (
    VoucherUsageFactory,
    PercentageDiscountVoucherFactory
)
from apps.users.factories import UserFactory


@pytest.mark.django_db
class TestVoucherUsage:
    """Test suite for VoucherUsage model."""

    def test_create_voucher_usage(self):
        """Test creating a voucher usage record."""
        # Arrange & Act
        usage = VoucherUsageFactory()

        # Assert
        assert usage.id is not None
        assert usage.voucher is not None
        assert usage.user is not None
        assert usage.purchase_amount > 0
        assert usage.discount_applied >= 0

    def test_voucher_usage_string_representation(self):
        """Test VoucherUsage __str__ method."""
        # Arrange
        user = UserFactory(email='test@example.com')
        voucher = PercentageDiscountVoucherFactory(code='TEST123')
        usage = VoucherUsageFactory(
            user=user,
            voucher=voucher
        )

        # Act
        result = str(usage)

        # Assert
        assert 'test@example.com' in result
        assert 'TEST123' in result

    def test_voucher_usage_relationships(self):
        """Test VoucherUsage relationships with voucher and user."""
        # Arrange
        voucher = PercentageDiscountVoucherFactory()
        user = UserFactory()

        # Act
        usage = VoucherUsageFactory(voucher=voucher, user=user)

        # Assert
        assert usage.voucher == voucher
        assert usage.user == user
        assert usage in voucher.usages.all()
        assert usage in user.voucher_usages.all()

    def test_voucher_usage_with_specific_amounts(self):
        """Test creating usage with specific amounts."""
        # Arrange & Act
        usage = VoucherUsageFactory(
            purchase_amount=Decimal('150.00'),
            discount_applied=Decimal('15.00')
        )

        # Assert
        assert usage.purchase_amount == Decimal('150.00')
        assert usage.discount_applied == Decimal('15.00')

    def test_voucher_usage_default_ordering(self):
        """Test voucher usages are ordered by used_at descending."""
        # Arrange
        usage1 = VoucherUsageFactory()
        usage2 = VoucherUsageFactory()
        usage3 = VoucherUsageFactory()

        # Act
        from apps.vouchers.models import VoucherUsage
        usages = VoucherUsage.objects.all()

        # Assert
        assert list(usages) == [usage3, usage2, usage1]

    def test_voucher_usage_meta_db_table(self):
        """Test VoucherUsage model uses correct database table."""
        # Arrange
        from apps.vouchers.models import VoucherUsage

        # Act & Assert
        assert VoucherUsage._meta.db_table == 'voucher_usages'

    def test_multiple_usages_for_same_voucher(self):
        """Test multiple users can use the same voucher."""
        # Arrange
        voucher = PercentageDiscountVoucherFactory()
        user1 = UserFactory()
        user2 = UserFactory()

        # Act
        usage1 = VoucherUsageFactory(voucher=voucher, user=user1)
        usage2 = VoucherUsageFactory(voucher=voucher, user=user2)

        # Assert
        assert voucher.usages.count() == 2
        assert usage1 in voucher.usages.all()
        assert usage2 in voucher.usages.all()

    def test_multiple_usages_for_same_user(self):
        """Test same user can use multiple vouchers."""
        # Arrange
        user = UserFactory()
        voucher1 = PercentageDiscountVoucherFactory()
        voucher2 = PercentageDiscountVoucherFactory()

        # Act
        usage1 = VoucherUsageFactory(voucher=voucher1, user=user)
        usage2 = VoucherUsageFactory(voucher=voucher2, user=user)

        # Assert
        assert user.voucher_usages.count() == 2
        assert usage1 in user.voucher_usages.all()
        assert usage2 in user.voucher_usages.all()

    def test_voucher_usage_cascade_delete_on_voucher(self):
        """Test usage is deleted when voucher is deleted."""
        # Arrange
        voucher = PercentageDiscountVoucherFactory()
        usage = VoucherUsageFactory(voucher=voucher)
        usage_id = usage.id

        # Act
        voucher.delete()

        # Assert
        from apps.vouchers.models import VoucherUsage
        assert not VoucherUsage.objects.filter(id=usage_id).exists()

    def test_voucher_usage_cascade_delete_on_user(self):
        """Test usage is deleted when user is deleted."""
        # Arrange
        user = UserFactory()
        usage = VoucherUsageFactory(user=user)
        usage_id = usage.id

        # Act
        user.delete()

        # Assert
        from apps.vouchers.models import VoucherUsage
        assert not VoucherUsage.objects.filter(id=usage_id).exists()

    def test_voucher_usage_used_at_auto_timestamp(self):
        """Test used_at is automatically set on creation."""
        # Arrange & Act
        usage = VoucherUsageFactory()

        # Assert
        assert usage.used_at is not None
