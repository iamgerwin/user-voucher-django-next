"""
Serializer for fixed amount discount vouchers.
"""

from decimal import Decimal

from rest_framework import serializers

from apps.vouchers.models import FixedAmountVoucher
from apps.vouchers.serializers.voucher import VoucherSerializer


class FixedAmountVoucherSerializer(VoucherSerializer):
    """
    Serializer for fixed amount discount vouchers.
    """

    class Meta(VoucherSerializer.Meta):
        model = FixedAmountVoucher
        fields = VoucherSerializer.Meta.fields + [
            'discount_amount',
            'min_purchase_amount',
        ]

    def validate_discount_amount(self, value):
        """
        Validate discount amount is positive.
        """
        if value <= Decimal('0'):
            raise serializers.ValidationError(
                "Discount amount must be greater than 0."
            )
        return value
