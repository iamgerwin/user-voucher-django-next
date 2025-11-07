"""
Voucher models package.
"""

from apps.vouchers.models.base import Voucher
from apps.vouchers.models.fixed_amount import FixedAmountVoucher
from apps.vouchers.models.free_shipping import FreeShippingVoucher
from apps.vouchers.models.percentage_discount import PercentageDiscountVoucher
from apps.vouchers.models.usage import VoucherUsage

__all__ = [
    'Voucher',
    'PercentageDiscountVoucher',
    'FixedAmountVoucher',
    'FreeShippingVoucher',
    'VoucherUsage',
]
