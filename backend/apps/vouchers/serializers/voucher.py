"""
Base serializer for all voucher types.
"""

from rest_framework import serializers

from apps.vouchers.models import Voucher


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
