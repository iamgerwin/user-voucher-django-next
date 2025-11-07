"""
Standard serializer for User model.
"""

from rest_framework import serializers

from apps.users.models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Standard serializer for User model.

    Excludes sensitive fields like password and provides proper validation.
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'phone_number',
            'role',
            'status',
            'is_active',
            'date_joined',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'date_joined',
            'created_at',
            'updated_at',
        ]

    def validate_email(self, value):
        """
        Validate email uniqueness during update.
        """
        if self.instance:
            # During update, check if email changed and if new email exists
            if value != self.instance.email and User.objects.filter(email=value).exists():
                raise serializers.ValidationError("A user with this email already exists.")
        return value


class UserListSerializer(serializers.ModelSerializer):
    """
    Minimal serializer for listing users (optimized for list views).
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'full_name',
            'role',
            'status',
            'date_joined',
        ]
        read_only_fields = fields


class UserAdminSerializer(serializers.ModelSerializer):
    """
    Admin serializer with additional fields and permissions.
    Only for admin users.
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    voucher_count = serializers.IntegerField(
        source='created_vouchers.count',
        read_only=True
    )
    voucher_usage_count = serializers.IntegerField(
        source='voucher_usages.count',
        read_only=True
    )

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'phone_number',
            'role',
            'status',
            'is_active',
            'is_staff',
            'is_superuser',
            'date_joined',
            'created_at',
            'updated_at',
            'voucher_count',
            'voucher_usage_count',
        ]
        read_only_fields = [
            'id',
            'date_joined',
            'created_at',
            'updated_at',
            'voucher_count',
            'voucher_usage_count',
        ]
