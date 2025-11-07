"""
Voucher factories for testing.
"""

from apps.vouchers.factories.percentage import PercentageDiscountVoucherFactory
from apps.vouchers.factories.fixed import FixedAmountVoucherFactory
from apps.vouchers.factories.free_shipping import FreeShippingVoucherFactory
from apps.vouchers.factories.usage import VoucherUsageFactory

__all__ = [
    'PercentageDiscountVoucherFactory',
    'FixedAmountVoucherFactory',
    'FreeShippingVoucherFactory',
    'VoucherUsageFactory',
]
