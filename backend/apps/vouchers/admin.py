"""
Admin configuration for Voucher models.
"""

from django.contrib import admin
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, PolymorphicChildModelFilter

from apps.vouchers.models import (
    Voucher,
    PercentageDiscountVoucher,
    FixedAmountVoucher,
    FreeShippingVoucher,
    VoucherUsage
)


class PercentageDiscountVoucherAdmin(PolymorphicChildModelAdmin):
    """Admin for PercentageDiscountVoucher."""
    base_model = PercentageDiscountVoucher
    show_in_index = True


class FixedAmountVoucherAdmin(PolymorphicChildModelAdmin):
    """Admin for FixedAmountVoucher."""
    base_model = FixedAmountVoucher
    show_in_index = True


class FreeShippingVoucherAdmin(PolymorphicChildModelAdmin):
    """Admin for FreeShippingVoucher."""
    base_model = FreeShippingVoucher
    show_in_index = True


@admin.register(Voucher)
class VoucherParentAdmin(PolymorphicParentModelAdmin):
    """
    Polymorphic admin for Voucher base model.
    """
    base_model = Voucher
    child_models = (PercentageDiscountVoucher, FixedAmountVoucher, FreeShippingVoucher)
    list_display = ('code', 'name', 'status', 'valid_from', 'valid_until', 'usage_count', 'usage_limit', 'created_by')
    list_filter = (PolymorphicChildModelFilter, 'status', 'valid_from', 'valid_until')
    search_fields = ('code', 'name', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('usage_count', 'created_at', 'updated_at')

    def get_queryset(self, request):
        """
        Optimize queryset with select_related to prevent N+1 queries.
        """
        qs = super().get_queryset(request)
        return qs.select_related('created_by')


@admin.register(VoucherUsage)
class VoucherUsageAdmin(admin.ModelAdmin):
    """
    Admin interface for VoucherUsage model.
    """
    list_display = ('voucher', 'user', 'purchase_amount', 'discount_applied', 'used_at')
    list_filter = ('used_at',)
    search_fields = ('voucher__code', 'user__email')
    ordering = ('-used_at',)
    readonly_fields = ('voucher', 'user', 'purchase_amount', 'discount_applied', 'used_at', 'created_at', 'updated_at')

    def get_queryset(self, request):
        """
        Optimize queryset with select_related to prevent N+1 queries.
        """
        qs = super().get_queryset(request)
        return qs.select_related('voucher', 'user')

    def has_add_permission(self, request):
        """Disable manual creation of voucher usage records."""
        return False

    def has_change_permission(self, request, obj=None):
        """Make voucher usage records read-only."""
        return False
