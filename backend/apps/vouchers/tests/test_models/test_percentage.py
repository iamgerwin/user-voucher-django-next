"""
Tests for PercentageDiscountVoucher model.
"""

from decimal import Decimal

import pytest

from apps.vouchers.factories import PercentageDiscountVoucherFactory


@pytest.mark.django_db
class TestPercentageDiscountVoucher:
    """Test suite for PercentageDiscountVoucher model."""

    def test_create_percentage_voucher(self):
        """Test creating a percentage discount voucher."""
        # Arrange & Act
        voucher = PercentageDiscountVoucherFactory(
            discount_percentage=Decimal('15.00')
        )

        # Assert
        assert voucher.discount_percentage == Decimal('15.00')

    def test_calculate_discount_basic(self):
        """Test basic discount calculation."""
        # Arrange
        voucher = PercentageDiscountVoucherFactory(
            discount_percentage=Decimal('10.00'),
            min_purchase_amount=Decimal('0.00')
        )

        # Act
        discount = voucher.calculate_discount(Decimal('100.00'))

        # Assert
        assert discount == Decimal('10.00')

    def test_calculate_discount_below_minimum(self):
        """Test discount is 0 when purchase is below minimum."""
        # Arrange
        voucher = PercentageDiscountVoucherFactory(
            discount_percentage=Decimal('20.00'),
            min_purchase_amount=Decimal('50.00')
        )

        # Act
        discount = voucher.calculate_discount(Decimal('30.00'))

        # Assert
        assert discount == Decimal('0.00')

    def test_calculate_discount_with_max_cap(self):
        """Test discount is capped at max_discount_amount."""
        # Arrange
        voucher = PercentageDiscountVoucherFactory(
            discount_percentage=Decimal('50.00'),
            max_discount_amount=Decimal('20.00'),
            min_purchase_amount=Decimal('0.00')
        )

        # Act
        discount = voucher.calculate_discount(Decimal('100.00'))

        # Assert
        # 50% of 100 = 50, but capped at 20
        assert discount == Decimal('20.00')

    def test_calculate_discount_without_max_cap(self):
        """Test discount without max cap."""
        # Arrange
        voucher = PercentageDiscountVoucherFactory(
            discount_percentage=Decimal('25.00'),
            max_discount_amount=None,
            min_purchase_amount=Decimal('0.00')
        )

        # Act
        discount = voucher.calculate_discount(Decimal('200.00'))

        # Assert
        assert discount == Decimal('50.00')

    def test_calculate_discount_exact_minimum(self):
        """Test discount when purchase equals minimum."""
        # Arrange
        voucher = PercentageDiscountVoucherFactory(
            discount_percentage=Decimal('15.00'),
            min_purchase_amount=Decimal('100.00')
        )

        # Act
        discount = voucher.calculate_discount(Decimal('100.00'))

        # Assert
        assert discount == Decimal('15.00')

    def test_calculate_discount_high_percentage(self):
        """Test discount with high percentage."""
        # Arrange
        voucher = PercentageDiscountVoucherFactory(
            discount_percentage=Decimal('100.00'),
            min_purchase_amount=Decimal('0.00')
        )

        # Act
        discount = voucher.calculate_discount(Decimal('50.00'))

        # Assert
        assert discount == Decimal('50.00')

    def test_calculate_discount_small_amount(self):
        """Test discount calculation with small amounts."""
        # Arrange
        voucher = PercentageDiscountVoucherFactory(
            discount_percentage=Decimal('10.00'),
            min_purchase_amount=Decimal('0.00')
        )

        # Act
        discount = voucher.calculate_discount(Decimal('9.99'))

        # Assert
        assert discount == Decimal('1.00')  # 0.999 rounded to 2 decimals

    def test_calculate_discount_precision(self):
        """Test discount calculation maintains precision."""
        # Arrange
        voucher = PercentageDiscountVoucherFactory(
            discount_percentage=Decimal('7.50'),
            min_purchase_amount=Decimal('0.00')
        )

        # Act
        discount = voucher.calculate_discount(Decimal('99.99'))

        # Assert
        # 7.5% of 99.99 = 7.49925, quantized to 7.50
        assert discount == Decimal('7.50')

    def test_percentage_voucher_polymorphic_type(self):
        """Test percentage voucher is correctly identified as polymorphic type."""
        # Arrange
        voucher = PercentageDiscountVoucherFactory()

        # Act
        from apps.vouchers.models import Voucher, PercentageDiscountVoucher
        base_voucher = Voucher.objects.get(id=voucher.id)

        # Assert
        assert isinstance(base_voucher, PercentageDiscountVoucher)
        assert base_voucher.polymorphic_ctype is not None
