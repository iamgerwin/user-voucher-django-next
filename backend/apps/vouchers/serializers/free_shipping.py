"""
Serializer for free shipping vouchers.
"""

from decimal import Decimal

from rest_framework import serializers

from apps.vouchers.models import FreeShippingVoucher
from apps.vouchers.serializers.voucher import VoucherSerializer


class FreeShippingVoucherSerializer(VoucherSerializer):
    """
    Serializer for free shipping vouchers.
    """

    class Meta(VoucherSerializer.Meta):
        model = FreeShippingVoucher
        fields = VoucherSerializer.Meta.fields + [
            'min_purchase_amount',
            'max_shipping_amount',
        ]

    def validate_max_shipping_amount(self, value):
        """
        Validate max shipping amount if provided.
        """
        if value is not None and value <= Decimal('0'):
            raise serializers.ValidationError(
                "Maximum shipping amount must be greater than 0."
            )
        return value
