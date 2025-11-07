"""
User serializers for REST API.
"""

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from apps.users.enums import UserRole, UserStatus
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


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new users with password handling.
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'password',
            'password_confirm',
            'first_name',
            'last_name',
            'phone_number',
            'role',
            'status',
        ]
        read_only_fields = ['id']
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, attrs):
        """
        Validate password confirmation.
        """
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': "Password fields didn't match."
            })
        attrs.pop('password_confirm')
        return attrs

    def create(self, validated_data):
        """
        Create user with proper password hashing.
        """
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user information (without password).
    """

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'phone_number',
        ]


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for changing user password.
    """
    old_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        """
        Validate passwords.
        """
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': "Password fields didn't match."
            })
        return attrs

    def validate_old_password(self, value):
        """
        Validate old password is correct.
        """
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
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
