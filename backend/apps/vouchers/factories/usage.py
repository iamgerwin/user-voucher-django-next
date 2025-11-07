"""
VoucherUsage factory for testing.
"""

from decimal import Decimal

import factory
from factory.django import DjangoModelFactory

from apps.vouchers.models import VoucherUsage


class VoucherUsageFactory(DjangoModelFactory):
    """
    Factory for creating VoucherUsage instances in tests.

    Usage:
        # Create a voucher usage record
        usage = VoucherUsageFactory()

        # Create with specific voucher and user
        usage = VoucherUsageFactory(voucher=voucher, user=user)

        # Create with specific amounts
        usage = VoucherUsageFactory(
            purchase_amount=Decimal('100.00'),
            discount_applied=Decimal('10.00')
        )
    """

    class Meta:
        model = VoucherUsage

    voucher = factory.SubFactory(
        'apps.vouchers.factories.PercentageDiscountVoucherFactory'
    )
    user = factory.SubFactory('apps.users.factories.UserFactory')

    purchase_amount = Decimal('100.00')
    discount_applied = Decimal('10.00')

    @factory.lazy_attribute
    def voucher(self):
        """
        Create a voucher for the usage if not provided.
        """
        from apps.vouchers.factories import PercentageDiscountVoucherFactory
        return PercentageDiscountVoucherFactory()

    @factory.lazy_attribute
    def user(self):
        """
        Create a user for the usage if not provided.
        """
        from apps.users.factories import UserFactory
        return UserFactory()
