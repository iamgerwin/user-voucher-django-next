"""
PercentageDiscountVoucher factory for testing.
"""

from decimal import Decimal

import factory
from django.utils import timezone
from factory.django import DjangoModelFactory

from apps.vouchers.enums import VoucherStatus
from apps.vouchers.models import PercentageDiscountVoucher


class PercentageDiscountVoucherFactory(DjangoModelFactory):
    """
    Factory for creating PercentageDiscountVoucher instances in tests.

    Usage:
        # Create a 10% discount voucher
        voucher = PercentageDiscountVoucherFactory(discount_percentage=10)

        # Create with usage limit
        voucher = PercentageDiscountVoucherFactory(usage_limit=100)

        # Create with max discount cap
        voucher = PercentageDiscountVoucherFactory(
            discount_percentage=20,
            max_discount_amount=Decimal('50.00')
        )
    """

    class Meta:
        model = PercentageDiscountVoucher
        django_get_or_create = ('code',)

    code = factory.Sequence(lambda n: f'PERCENT{n:04d}')
    name = factory.Faker('catch_phrase')
    description = factory.Faker('text', max_nb_chars=200)
    status = VoucherStatus.ACTIVE

    valid_from = factory.LazyFunction(timezone.now)
    valid_until = factory.LazyFunction(
        lambda: timezone.now() + timezone.timedelta(days=30)
    )

    usage_limit = None
    usage_count = 0

    discount_percentage = Decimal('10.00')
    max_discount_amount = None
    min_purchase_amount = Decimal('0.00')

    created_by = factory.SubFactory('apps.users.factories.UserFactory')

    @factory.lazy_attribute
    def created_by(self):
        """
        Create a user for created_by if not provided.
        """
        from apps.users.factories import UserFactory
        return UserFactory()
