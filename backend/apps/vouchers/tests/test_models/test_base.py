"""
Tests for base Voucher model.
"""

from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.vouchers.enums import VoucherStatus
from apps.vouchers.factories import PercentageDiscountVoucherFactory
from apps.users.factories import UserFactory


@pytest.mark.django_db
class TestVoucherModel:
    """Test suite for base Voucher model."""

    def test_create_voucher_with_factory(self):
        """Test creating a voucher with factory."""
        # Arrange & Act
        voucher = PercentageDiscountVoucherFactory()

        # Assert
        assert voucher.id is not None
        assert voucher.code is not None
        assert voucher.name is not None
        assert voucher.status == VoucherStatus.ACTIVE
        assert voucher.created_by is not None

    def test_voucher_string_representation(self):
        """Test Voucher __str__ method."""
        # Arrange
        voucher = PercentageDiscountVoucherFactory(
            code='TEST123',
            name='Test Voucher'
        )

        # Act
        result = str(voucher)

        # Assert
        assert result == 'TEST123 - Test Voucher'

    def test_voucher_code_uniqueness(self):
        """Test voucher code must be unique."""
        # Arrange
        code = 'UNIQUE123'
        voucher1 = PercentageDiscountVoucherFactory(code=code)

        # Act & Assert
        # Factory uses get_or_create, so create directly to test constraint
        from django.db import IntegrityError
        from apps.vouchers.models import PercentageDiscountVoucher
        from django.utils import timezone

        with pytest.raises(IntegrityError):
            PercentageDiscountVoucher.objects.create(
                code=code,
                name='Test',
                status=VoucherStatus.ACTIVE,
                valid_from=timezone.now(),
                valid_until=timezone.now() + timezone.timedelta(days=30),
                discount_percentage=Decimal('10.00'),
                created_by=voucher1.created_by
            )

    def test_is_valid_property_active_voucher(self):
        """Test is_valid property for active voucher within valid dates."""
        # Arrange
        now = timezone.now()
        voucher = PercentageDiscountVoucherFactory(
            status=VoucherStatus.ACTIVE,
            valid_from=now - timezone.timedelta(days=1),
            valid_until=now + timezone.timedelta(days=1),
            usage_limit=10,
            usage_count=5
        )

        # Act & Assert
        assert voucher.is_valid is True

    def test_is_valid_property_inactive_voucher(self):
        """Test is_valid property for inactive voucher."""
        # Arrange
        now = timezone.now()
        voucher = PercentageDiscountVoucherFactory(
            status=VoucherStatus.EXPIRED,
            valid_from=now - timezone.timedelta(days=1),
            valid_until=now + timezone.timedelta(days=1)
        )

        # Act & Assert
        assert voucher.is_valid is False

    def test_is_valid_property_before_valid_from(self):
        """Test is_valid property for voucher before valid_from date."""
        # Arrange
        now = timezone.now()
        voucher = PercentageDiscountVoucherFactory(
            status=VoucherStatus.ACTIVE,
            valid_from=now + timezone.timedelta(days=1),
            valid_until=now + timezone.timedelta(days=2)
        )

        # Act & Assert
        assert voucher.is_valid is False

    def test_is_valid_property_after_valid_until(self):
        """Test is_valid property for voucher after valid_until date."""
        # Arrange
        now = timezone.now()
        voucher = PercentageDiscountVoucherFactory(
            status=VoucherStatus.ACTIVE,
            valid_from=now - timezone.timedelta(days=2),
            valid_until=now - timezone.timedelta(days=1)
        )

        # Act & Assert
        assert voucher.is_valid is False

    def test_is_valid_property_usage_limit_reached(self):
        """Test is_valid property when usage limit is reached."""
        # Arrange
        now = timezone.now()
        voucher = PercentageDiscountVoucherFactory(
            status=VoucherStatus.ACTIVE,
            valid_from=now - timezone.timedelta(days=1),
            valid_until=now + timezone.timedelta(days=1),
            usage_limit=10,
            usage_count=10
        )

        # Act & Assert
        assert voucher.is_valid is False

    def test_is_valid_property_unlimited_usage(self):
        """Test is_valid property with unlimited usage."""
        # Arrange
        now = timezone.now()
        voucher = PercentageDiscountVoucherFactory(
            status=VoucherStatus.ACTIVE,
            valid_from=now - timezone.timedelta(days=1),
            valid_until=now + timezone.timedelta(days=1),
            usage_limit=None,
            usage_count=1000
        )

        # Act & Assert
        assert voucher.is_valid is True

    def test_is_expired_property(self):
        """Test is_expired property."""
        # Arrange
        now = timezone.now()
        expired_voucher = PercentageDiscountVoucherFactory(
            valid_from=now - timezone.timedelta(days=2),
            valid_until=now - timezone.timedelta(days=1)
        )
        valid_voucher = PercentageDiscountVoucherFactory(
            valid_from=now - timezone.timedelta(days=1),
            valid_until=now + timezone.timedelta(days=1)
        )

        # Act & Assert
        assert expired_voucher.is_expired is True
        assert valid_voucher.is_expired is False

    def test_increment_usage(self):
        """Test increment_usage method."""
        # Arrange
        voucher = PercentageDiscountVoucherFactory(
            usage_limit=None,
            usage_count=5
        )

        # Act
        voucher.increment_usage()

        # Assert
        voucher.refresh_from_db()
        assert voucher.usage_count == 6
        assert voucher.status == VoucherStatus.ACTIVE

    def test_increment_usage_reaches_limit(self):
        """Test increment_usage marks voucher as used when limit reached."""
        # Arrange
        voucher = PercentageDiscountVoucherFactory(
            usage_limit=10,
            usage_count=9
        )

        # Act
        voucher.increment_usage()

        # Assert
        voucher.refresh_from_db()
        assert voucher.usage_count == 10
        assert voucher.status == VoucherStatus.USED

    def test_clean_validation_invalid_dates(self):
        """Test clean() validation fails when valid_until <= valid_from."""
        # Arrange
        now = timezone.now()
        voucher = PercentageDiscountVoucherFactory.build(
            valid_from=now + timezone.timedelta(days=2),
            valid_until=now + timezone.timedelta(days=1)
        )

        # Act & Assert
        with pytest.raises(ValidationError, match='Valid until date must be after valid from date'):
            voucher.clean()

    def test_voucher_default_ordering(self):
        """Test vouchers are ordered by created_at descending."""
        # Arrange
        voucher1 = PercentageDiscountVoucherFactory()
        voucher2 = PercentageDiscountVoucherFactory()
        voucher3 = PercentageDiscountVoucherFactory()

        # Act
        from apps.vouchers.models import Voucher
        vouchers = Voucher.objects.all()

        # Assert
        assert list(vouchers) == [voucher3, voucher2, voucher1]

    def test_voucher_meta_db_table(self):
        """Test Voucher model uses correct database table."""
        # Arrange
        from apps.vouchers.models import Voucher

        # Act & Assert
        assert Voucher._meta.db_table == 'vouchers'

    def test_voucher_created_by_relationship(self):
        """Test voucher created_by relationship."""
        # Arrange
        user = UserFactory()
        voucher = PercentageDiscountVoucherFactory(created_by=user)

        # Act & Assert
        assert voucher.created_by == user
        assert voucher in user.created_vouchers.all()

    def test_voucher_created_by_set_null_on_delete(self):
        """Test created_by is set to null when user is deleted."""
        # Arrange
        user = UserFactory()
        voucher = PercentageDiscountVoucherFactory(created_by=user)
        voucher_id = voucher.id

        # Act
        user.delete()

        # Assert
        from apps.vouchers.models import Voucher
        voucher = Voucher.objects.get(id=voucher_id)
        assert voucher.created_by is None
