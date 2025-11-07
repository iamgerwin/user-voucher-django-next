"""
FreeShippingVoucher factory for testing.
"""

from decimal import Decimal

import factory
from django.utils import timezone
from factory.django import DjangoModelFactory

from apps.vouchers.enums import VoucherStatus
from apps.vouchers.models import FreeShippingVoucher


class FreeShippingVoucherFactory(DjangoModelFactory):
    """
    Factory for creating FreeShippingVoucher instances in tests.

    Usage:
        # Create a free shipping voucher
        voucher = FreeShippingVoucherFactory()

        # Create with minimum purchase requirement
        voucher = FreeShippingVoucherFactory(min_purchase_amount=Decimal('50.00'))

        # Create with max shipping cap
        voucher = FreeShippingVoucherFactory(max_shipping_amount=Decimal('15.00'))
    """

    class Meta:
        model = FreeShippingVoucher
        django_get_or_create = ('code',)

    code = factory.Sequence(lambda n: f'FREESHIP{n:04d}')
    name = factory.Faker('catch_phrase')
    description = factory.Faker('text', max_nb_chars=200)
    status = VoucherStatus.ACTIVE

    valid_from = factory.LazyFunction(timezone.now)
    valid_until = factory.LazyFunction(
        lambda: timezone.now() + timezone.timedelta(days=30)
    )

    usage_limit = None
    usage_count = 0

    min_purchase_amount = Decimal('0.00')
    max_shipping_amount = None

    created_by = factory.SubFactory('apps.users.factories.UserFactory')

    @factory.lazy_attribute
    def created_by(self):
        """
        Create a user for created_by if not provided.
        """
        from apps.users.factories import UserFactory
        return UserFactory()
