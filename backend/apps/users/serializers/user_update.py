"""
Serializer for updating user information (without password).
"""

from rest_framework import serializers

from apps.users.models import User


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
