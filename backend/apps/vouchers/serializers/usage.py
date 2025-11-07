"""
Serializers for voucher usage tracking.
"""

from decimal import Decimal

from rest_framework import serializers

from apps.vouchers.enums import VoucherStatus
from apps.vouchers.models import Voucher, VoucherUsage


class VoucherUsageSerializer(serializers.ModelSerializer):
    """
    Serializer for voucher usage tracking.
    """
    voucher_code = serializers.CharField(source='voucher.code', read_only=True)
    voucher_name = serializers.CharField(source='voucher.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = VoucherUsage
        fields = [
            'id',
            'voucher',
            'voucher_code',
            'voucher_name',
            'user',
            'user_email',
            'user_name',
            'purchase_amount',
            'discount_applied',
            'used_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'used_at',
            'created_at',
            'updated_at',
        ]

    def validate_purchase_amount(self, value):
        """
        Validate purchase amount is positive.
        """
        if value < Decimal('0'):
            raise serializers.ValidationError(
                "Purchase amount must be greater than or equal to 0."
            )
        return value

    def validate_discount_applied(self, value):
        """
        Validate discount applied is positive.
        """
        if value < Decimal('0'):
            raise serializers.ValidationError(
                "Discount applied must be greater than or equal to 0."
            )
        return value


class VoucherUsageCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating voucher usage records.
    """
    voucher_code = serializers.CharField(write_only=True)

    class Meta:
        model = VoucherUsage
        fields = [
            'voucher_code',
            'purchase_amount',
            'discount_applied',
        ]

    def validate_voucher_code(self, value):
        """
        Validate voucher exists and is valid.
        """
        try:
            voucher = Voucher.objects.get(code=value.upper())
        except Voucher.DoesNotExist:
            raise serializers.ValidationError("Voucher with this code does not exist.")

        if not voucher.is_valid:
            if voucher.status != VoucherStatus.ACTIVE:
                raise serializers.ValidationError(
                    f"Voucher is not active. Current status: {voucher.get_status_display()}"
                )
            elif voucher.is_expired:
                raise serializers.ValidationError("Voucher has expired.")
            elif voucher.usage_limit and voucher.usage_count >= voucher.usage_limit:
                raise serializers.ValidationError("Voucher usage limit has been reached.")
            else:
                raise serializers.ValidationError("Voucher is not valid for use.")

        return value

    def create(self, validated_data):
        """
        Create voucher usage and increment voucher usage count.
        """
        voucher_code = validated_data.pop('voucher_code')
        voucher = Voucher.objects.get(code=voucher_code.upper())

        # Create usage record
        usage = VoucherUsage.objects.create(
            voucher=voucher,
            user=self.context['request'].user,
            **validated_data
        )

        # Increment voucher usage count
        voucher.increment_usage()

        return usage


class VoucherValidateSerializer(serializers.Serializer):
    """
    Serializer for validating voucher codes.
    """
    code = serializers.CharField(required=True)
    purchase_amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        min_value=Decimal('0')
    )
    shipping_amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        min_value=Decimal('0')
    )

    def validate(self, attrs):
        """
        Validate voucher and calculate potential discount.
        """
        from apps.vouchers.models import (
            PercentageDiscountVoucher,
            FixedAmountVoucher,
            FreeShippingVoucher,
        )

        code = attrs.get('code', '').upper()
        purchase_amount = attrs.get('purchase_amount', Decimal('0'))
        shipping_amount = attrs.get('shipping_amount', Decimal('0'))

        try:
            voucher = Voucher.objects.get(code=code)
        except Voucher.DoesNotExist:
            raise serializers.ValidationError({
                'code': 'Voucher with this code does not exist.'
            })

        # Check if voucher is valid
        if not voucher.is_valid:
            error_message = 'Voucher is not valid.'
            if voucher.status != VoucherStatus.ACTIVE:
                error_message = f'Voucher is {voucher.get_status_display().lower()}.'
            elif voucher.is_expired:
                error_message = 'Voucher has expired.'
            elif voucher.usage_limit and voucher.usage_count >= voucher.usage_limit:
                error_message = 'Voucher usage limit has been reached.'

            raise serializers.ValidationError({'code': error_message})

        # Calculate discount based on voucher type
        discount = Decimal('0')
        if isinstance(voucher, PercentageDiscountVoucher):
            if purchase_amount >= voucher.min_purchase_amount:
                discount = voucher.calculate_discount(purchase_amount)
        elif isinstance(voucher, FixedAmountVoucher):
            if purchase_amount >= voucher.min_purchase_amount:
                discount = voucher.calculate_discount(purchase_amount)
        elif isinstance(voucher, FreeShippingVoucher):
            if purchase_amount >= voucher.min_purchase_amount:
                discount = voucher.calculate_discount(purchase_amount, shipping_amount)

        attrs['voucher'] = voucher
        attrs['calculated_discount'] = discount

        return attrs
