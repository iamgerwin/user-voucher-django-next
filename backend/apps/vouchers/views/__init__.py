"""
Voucher viewsets package.
"""

from apps.vouchers.views.fixed_viewset import FixedAmountVoucherViewSet
from apps.vouchers.views.free_shipping_viewset import FreeShippingVoucherViewSet
from apps.vouchers.views.percentage_viewset import PercentageDiscountVoucherViewSet
from apps.vouchers.views.usage_viewset import VoucherUsageViewSet
from apps.vouchers.views.voucher_viewset import VoucherViewSet

__all__ = [
    'VoucherViewSet',
    'PercentageDiscountVoucherViewSet',
    'FixedAmountVoucherViewSet',
    'FreeShippingVoucherViewSet',
    'VoucherUsageViewSet',
]
