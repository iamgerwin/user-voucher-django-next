"""
Tests for FreeShippingVoucher model.
"""

from decimal import Decimal

import pytest

from apps.vouchers.factories import FreeShippingVoucherFactory


@pytest.mark.django_db
class TestFreeShippingVoucher:
    """Test suite for FreeShippingVoucher model."""

    def test_create_free_shipping_voucher(self):
        """Test creating a free shipping voucher."""
        # Arrange & Act
        voucher = FreeShippingVoucherFactory()

        # Assert
        assert voucher.min_purchase_amount == Decimal('0.00')

    def test_calculate_discount_basic(self):
        """Test basic shipping discount calculation."""
        # Arrange
        voucher = FreeShippingVoucherFactory(
            min_purchase_amount=Decimal('0.00'),
            max_shipping_amount=None
        )

        # Act
        discount = voucher.calculate_discount(
            purchase_amount=Decimal('100.00'),
            shipping_amount=Decimal('15.00')
        )

        # Assert
        assert discount == Decimal('15.00')

    def test_calculate_discount_below_minimum(self):
        """Test discount is 0 when purchase is below minimum."""
        # Arrange
        voucher = FreeShippingVoucherFactory(
            min_purchase_amount=Decimal('50.00'),
            max_shipping_amount=None
        )

        # Act
        discount = voucher.calculate_discount(
            purchase_amount=Decimal('30.00'),
            shipping_amount=Decimal('10.00')
        )

        # Assert
        assert discount == Decimal('0.00')

    def test_calculate_discount_with_max_cap(self):
        """Test discount is capped at max_shipping_amount."""
        # Arrange
        voucher = FreeShippingVoucherFactory(
            min_purchase_amount=Decimal('0.00'),
            max_shipping_amount=Decimal('10.00')
        )

        # Act
        discount = voucher.calculate_discount(
            purchase_amount=Decimal('100.00'),
            shipping_amount=Decimal('25.00')
        )

        # Assert
        # Shipping is 25 but capped at 10
        assert discount == Decimal('10.00')

    def test_calculate_discount_without_max_cap(self):
        """Test discount without max cap covers full shipping."""
        # Arrange
        voucher = FreeShippingVoucherFactory(
            min_purchase_amount=Decimal('0.00'),
            max_shipping_amount=None
        )

        # Act
        discount = voucher.calculate_discount(
            purchase_amount=Decimal('100.00'),
            shipping_amount=Decimal('50.00')
        )

        # Assert
        assert discount == Decimal('50.00')

    def test_calculate_discount_exact_minimum(self):
        """Test discount when purchase equals minimum."""
        # Arrange
        voucher = FreeShippingVoucherFactory(
            min_purchase_amount=Decimal('100.00'),
            max_shipping_amount=None
        )

        # Act
        discount = voucher.calculate_discount(
            purchase_amount=Decimal('100.00'),
            shipping_amount=Decimal('15.00')
        )

        # Assert
        assert discount == Decimal('15.00')

    def test_calculate_discount_shipping_below_cap(self):
        """Test discount when shipping is below max cap."""
        # Arrange
        voucher = FreeShippingVoucherFactory(
            min_purchase_amount=Decimal('0.00'),
            max_shipping_amount=Decimal('20.00')
        )

        # Act
        discount = voucher.calculate_discount(
            purchase_amount=Decimal('100.00'),
            shipping_amount=Decimal('10.00')
        )

        # Assert
        # Shipping is 10, max is 20, so return 10
        assert discount == Decimal('10.00')

    def test_calculate_discount_zero_shipping(self):
        """Test discount with zero shipping cost."""
        # Arrange
        voucher = FreeShippingVoucherFactory(
            min_purchase_amount=Decimal('0.00'),
            max_shipping_amount=None
        )

        # Act
        discount = voucher.calculate_discount(
            purchase_amount=Decimal('100.00'),
            shipping_amount=Decimal('0.00')
        )

        # Assert
        assert discount == Decimal('0.00')

    def test_calculate_discount_high_minimum_requirement(self):
        """Test discount with high minimum purchase requirement."""
        # Arrange
        voucher = FreeShippingVoucherFactory(
            min_purchase_amount=Decimal('200.00'),
            max_shipping_amount=None
        )

        # Act
        discount_below = voucher.calculate_discount(
            purchase_amount=Decimal('150.00'),
            shipping_amount=Decimal('20.00')
        )
        discount_above = voucher.calculate_discount(
            purchase_amount=Decimal('250.00'),
            shipping_amount=Decimal('20.00')
        )

        # Assert
        assert discount_below == Decimal('0.00')
        assert discount_above == Decimal('20.00')

    def test_free_shipping_voucher_polymorphic_type(self):
        """Test free shipping voucher is correctly identified as polymorphic type."""
        # Arrange
        voucher = FreeShippingVoucherFactory()

        # Act
        from apps.vouchers.models import Voucher, FreeShippingVoucher
        base_voucher = Voucher.objects.get(id=voucher.id)

        # Assert
        assert isinstance(base_voucher, FreeShippingVoucher)
        assert base_voucher.polymorphic_ctype is not None
