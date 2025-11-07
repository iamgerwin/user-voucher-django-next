"""
Tests for FixedAmountVoucher model.
"""

from decimal import Decimal

import pytest

from apps.vouchers.factories import FixedAmountVoucherFactory


@pytest.mark.django_db
class TestFixedAmountVoucher:
    """Test suite for FixedAmountVoucher model."""

    def test_create_fixed_amount_voucher(self):
        """Test creating a fixed amount voucher."""
        # Arrange & Act
        voucher = FixedAmountVoucherFactory(
            discount_amount=Decimal('25.00')
        )

        # Assert
        assert voucher.discount_amount == Decimal('25.00')

    def test_calculate_discount_basic(self):
        """Test basic discount calculation."""
        # Arrange
        voucher = FixedAmountVoucherFactory(
            discount_amount=Decimal('10.00'),
            min_purchase_amount=Decimal('0.00')
        )

        # Act
        discount = voucher.calculate_discount(Decimal('100.00'))

        # Assert
        assert discount == Decimal('10.00')

    def test_calculate_discount_below_minimum(self):
        """Test discount is 0 when purchase is below minimum."""
        # Arrange
        voucher = FixedAmountVoucherFactory(
            discount_amount=Decimal('15.00'),
            min_purchase_amount=Decimal('50.00')
        )

        # Act
        discount = voucher.calculate_discount(Decimal('30.00'))

        # Assert
        assert discount == Decimal('0.00')

    def test_calculate_discount_capped_at_purchase_amount(self):
        """Test discount cannot exceed purchase amount."""
        # Arrange
        voucher = FixedAmountVoucherFactory(
            discount_amount=Decimal('50.00'),
            min_purchase_amount=Decimal('0.00')
        )

        # Act
        discount = voucher.calculate_discount(Decimal('30.00'))

        # Assert
        # Discount should be capped at purchase amount
        assert discount == Decimal('30.00')

    def test_calculate_discount_exact_purchase_amount(self):
        """Test discount when it equals purchase amount."""
        # Arrange
        voucher = FixedAmountVoucherFactory(
            discount_amount=Decimal('100.00'),
            min_purchase_amount=Decimal('0.00')
        )

        # Act
        discount = voucher.calculate_discount(Decimal('100.00'))

        # Assert
        assert discount == Decimal('100.00')

    def test_calculate_discount_with_minimum_requirement(self):
        """Test discount with minimum purchase requirement."""
        # Arrange
        voucher = FixedAmountVoucherFactory(
            discount_amount=Decimal('20.00'),
            min_purchase_amount=Decimal('100.00')
        )

        # Act
        discount_below = voucher.calculate_discount(Decimal('99.99'))
        discount_exact = voucher.calculate_discount(Decimal('100.00'))
        discount_above = voucher.calculate_discount(Decimal('150.00'))

        # Assert
        assert discount_below == Decimal('0.00')
        assert discount_exact == Decimal('20.00')
        assert discount_above == Decimal('20.00')

    def test_calculate_discount_small_amounts(self):
        """Test discount with small amounts."""
        # Arrange
        voucher = FixedAmountVoucherFactory(
            discount_amount=Decimal('5.00'),
            min_purchase_amount=Decimal('0.00')
        )

        # Act
        discount = voucher.calculate_discount(Decimal('10.00'))

        # Assert
        assert discount == Decimal('5.00')

    def test_calculate_discount_large_amounts(self):
        """Test discount with large amounts."""
        # Arrange
        voucher = FixedAmountVoucherFactory(
            discount_amount=Decimal('100.00'),
            min_purchase_amount=Decimal('0.00')
        )

        # Act
        discount = voucher.calculate_discount(Decimal('1000.00'))

        # Assert
        assert discount == Decimal('100.00')

    def test_fixed_voucher_polymorphic_type(self):
        """Test fixed voucher is correctly identified as polymorphic type."""
        # Arrange
        voucher = FixedAmountVoucherFactory()

        # Act
        from apps.vouchers.models import Voucher, FixedAmountVoucher
        base_voucher = Voucher.objects.get(id=voucher.id)

        # Assert
        assert isinstance(base_voucher, FixedAmountVoucher)
        assert base_voucher.polymorphic_ctype is not None
