"""
Unified serializer for creating vouchers with polymorphic type handling.
"""

from decimal import Decimal
from django.utils import timezone
from rest_framework import serializers

from apps.vouchers.models import (
    FixedAmountVoucher,
    PercentageDiscountVoucher,
)
from apps.vouchers.enums import VoucherStatus, DiscountType


class VoucherCreateSerializer(serializers.Serializer):
    """
    Unified serializer for creating vouchers.

    Accepts a discount_type field to determine which polymorphic type to create.
    Supports optional validity dates for vouchers valid indefinitely.
    """
    code = serializers.CharField(
        max_length=50,
        help_text='Unique voucher code'
    )
    name = serializers.CharField(
        max_length=200,
        required=False,
        help_text='Human-readable voucher name (defaults to code if not provided)'
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        default='',
        help_text='Detailed description of the voucher'
    )
    discount_type = serializers.ChoiceField(
        choices=[
            (DiscountType.FIXED_AMOUNT.value, 'Fixed Amount'),
            (DiscountType.PERCENTAGE.value, 'Percentage'),
        ],
        help_text='Type of discount: fixed amount or percentage'
    )
    discount_amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Discount amount (dollar amount for fixed, percentage 0-100 for percentage)'
    )
    max_uses = serializers.IntegerField(
        required=False,
        min_value=1,
        help_text='Maximum number of times this voucher can be used (usage_limit)'
    )
    valid_from = serializers.DateTimeField(
        required=False,
        allow_null=True,
        help_text='Date when voucher becomes valid'
    )
    valid_until = serializers.DateTimeField(
        required=False,
        allow_null=True,
        help_text='Date when voucher expires'
    )
    valid_indefinitely = serializers.BooleanField(
        required=False,
        default=False,
        help_text='Whether the voucher is valid indefinitely'
    )
    status = serializers.ChoiceField(
        choices=VoucherStatus.choices,
        default=VoucherStatus.ACTIVE,
        required=False,
        help_text='Initial status of the voucher'
    )

    def validate_code(self, value):
        """Validate voucher code uniqueness."""
        value = value.upper()

        # Check if code already exists
        if FixedAmountVoucher.objects.filter(code=value).exists():
            raise serializers.ValidationError("A voucher with this code already exists.")
        if PercentageDiscountVoucher.objects.filter(code=value).exists():
            raise serializers.ValidationError("A voucher with this code already exists.")

        return value

    def validate_discount_amount(self, value):
        """Validate discount amount is positive."""
        if value <= Decimal('0'):
            raise serializers.ValidationError("Discount amount must be greater than 0.")
        return value

    def validate(self, attrs):
        """Validate the entire voucher creation request."""
        discount_type = attrs.get('discount_type')
        discount_amount = attrs.get('discount_amount')
        valid_indefinitely = attrs.get('valid_indefinitely', False)
        valid_from = attrs.get('valid_from')
        valid_until = attrs.get('valid_until')

        # Validate percentage discount is between 0-100
        if discount_type == DiscountType.PERCENTAGE.value:
            if discount_amount > Decimal('100'):
                raise serializers.ValidationError({
                    'discount_amount': 'Percentage discount cannot exceed 100.'
                })

        # If both dates are missing, treat as valid indefinitely
        if not valid_from and not valid_until:
            valid_indefinitely = True
            attrs['valid_indefinitely'] = True

        # Validate validity dates
        if not valid_indefinitely:
            # If one date is provided, both must be provided
            if not valid_from or not valid_until:
                raise serializers.ValidationError({
                    'valid_from': 'Both valid from and until dates are required.',
                    'valid_until': 'Both valid from and until dates are required.',
                })

            if valid_until <= valid_from:
                raise serializers.ValidationError({
                    'valid_until': 'Valid until date must be after valid from date.'
                })
        else:
            # Set default dates for indefinite vouchers if not provided
            if not valid_from:
                attrs['valid_from'] = timezone.now()
            if not valid_until:
                # Set to a far future date (100 years from now)
                attrs['valid_until'] = timezone.now() + timezone.timedelta(days=36500)

        # Set default name to code if not provided
        if not attrs.get('name'):
            attrs['name'] = attrs['code']

        return attrs

    def create(self, validated_data):
        """
        Create the appropriate voucher type based on discount_type.
        """
        discount_type = validated_data.pop('discount_type')
        discount_amount = validated_data.pop('discount_amount')
        max_uses = validated_data.pop('max_uses', None)
        valid_indefinitely = validated_data.pop('valid_indefinitely', False)

        # Map max_uses to usage_limit
        validated_data['usage_limit'] = max_uses

        # Create the appropriate voucher type
        if discount_type == DiscountType.FIXED_AMOUNT.value:
            voucher = FixedAmountVoucher.objects.create(
                **validated_data,
                discount_amount=discount_amount,
                min_purchase_amount=Decimal('0.00')
            )
        else:  # percentage
            voucher = PercentageDiscountVoucher.objects.create(
                **validated_data,
                discount_percentage=discount_amount,
                min_purchase_amount=Decimal('0.00')
            )

        return voucher
