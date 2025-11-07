"""
Voucher serializers for REST API with polymorphic support.
"""

from decimal import Decimal

from django.utils import timezone
from rest_framework import serializers

from apps.vouchers.enums import VoucherStatus, DiscountType
from apps.vouchers.models import (
    Voucher,
    PercentageDiscountVoucher,
    FixedAmountVoucher,
    FreeShippingVoucher,
    VoucherUsage,
)


class VoucherSerializer(serializers.ModelSerializer):
    """
    Base serializer for all voucher types.

    Provides common fields and validation for polymorphic voucher models.
    """
    voucher_type = serializers.SerializerMethodField()
    is_valid = serializers.BooleanField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    created_by_name = serializers.CharField(
        source='created_by.get_full_name',
        read_only=True
    )
    usage_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Voucher
        fields = [
            'id',
            'code',
            'name',
            'description',
            'status',
            'valid_from',
            'valid_until',
            'usage_limit',
            'usage_count',
            'usage_percentage',
            'created_by',
            'created_by_name',
            'created_at',
            'updated_at',
            'voucher_type',
            'is_valid',
            'is_expired',
        ]
        read_only_fields = [
            'id',
            'usage_count',
            'created_at',
            'updated_at',
            'is_valid',
            'is_expired',
        ]
        extra_kwargs = {
            'created_by': {'required': False},
        }

    def get_voucher_type(self, obj):
        """
        Return the type of voucher (polymorphic type name).
        """
        return obj.polymorphic_ctype.model

    def get_usage_percentage(self, obj):
        """
        Calculate usage percentage if usage_limit exists.
        """
        if obj.usage_limit:
            return round((obj.usage_count / obj.usage_limit) * 100, 2)
        return None

    def validate(self, attrs):
        """
        Validate voucher dates and other business logic.
        """
        valid_from = attrs.get('valid_from', getattr(self.instance, 'valid_from', None))
        valid_until = attrs.get('valid_until', getattr(self.instance, 'valid_until', None))

        if valid_from and valid_until and valid_until <= valid_from:
            raise serializers.ValidationError({
                'valid_until': 'Valid until date must be after valid from date.'
            })

        return attrs

    def validate_code(self, value):
        """
        Validate voucher code uniqueness.
        """
        # Convert to uppercase for consistency
        value = value.upper()

        # Check uniqueness during create
        if not self.instance and Voucher.objects.filter(code=value).exists():
            raise serializers.ValidationError("A voucher with this code already exists.")

        # Check uniqueness during update
        if self.instance and value != self.instance.code:
            if Voucher.objects.filter(code=value).exists():
                raise serializers.ValidationError("A voucher with this code already exists.")

        return value


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


class VoucherListSerializer(serializers.ModelSerializer):
    """
    Minimal serializer for listing vouchers (optimized for list views).
    """
    voucher_type = serializers.SerializerMethodField()
    is_valid = serializers.BooleanField(read_only=True)

    class Meta:
        model = Voucher
        fields = [
            'id',
            'code',
            'name',
            'status',
            'valid_from',
            'valid_until',
            'usage_count',
            'usage_limit',
            'voucher_type',
            'is_valid',
        ]
        read_only_fields = fields

    def get_voucher_type(self, obj):
        """
        Return the type of voucher.
        """
        return obj.polymorphic_ctype.model


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
