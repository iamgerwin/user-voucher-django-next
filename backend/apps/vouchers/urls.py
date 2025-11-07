"""
URL routing for vouchers app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.vouchers.views import (
    VoucherViewSet,
    PercentageDiscountVoucherViewSet,
    FixedAmountVoucherViewSet,
    FreeShippingVoucherViewSet,
    VoucherUsageViewSet,
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'vouchers', VoucherViewSet, basename='voucher')
router.register(r'percentage-vouchers', PercentageDiscountVoucherViewSet, basename='percentage-voucher')
router.register(r'fixed-amount-vouchers', FixedAmountVoucherViewSet, basename='fixed-amount-voucher')
router.register(r'free-shipping-vouchers', FreeShippingVoucherViewSet, basename='free-shipping-voucher')
router.register(r'voucher-usages', VoucherUsageViewSet, basename='voucher-usage')

# URL patterns
urlpatterns = [
    path('', include(router.urls)),
]
