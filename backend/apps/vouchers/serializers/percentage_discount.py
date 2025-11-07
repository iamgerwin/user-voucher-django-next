"""
Serializer for percentage discount vouchers.
"""

from decimal import Decimal

from rest_framework import serializers

from apps.vouchers.models import PercentageDiscountVoucher
from apps.vouchers.serializers.voucher import VoucherSerializer


class PercentageDiscountVoucherSerializer(VoucherSerializer):
    """
    Serializer for percentage discount vouchers.
    """

    class Meta(VoucherSerializer.Meta):
        model = PercentageDiscountVoucher
        fields = VoucherSerializer.Meta.fields + [
            'discount_percentage',
            'max_discount_amount',
            'min_purchase_amount',
        ]

    def validate_discount_percentage(self, value):
        """
        Validate discount percentage is within valid range.
        """
        if value <= Decimal('0') or value > Decimal('100'):
            raise serializers.ValidationError(
                "Discount percentage must be between 0.01 and 100."
            )
        return value

    def validate_max_discount_amount(self, value):
        """
        Validate max discount amount if provided.
        """
        if value is not None and value <= Decimal('0'):
            raise serializers.ValidationError(
                "Maximum discount amount must be greater than 0."
            )
        return value
