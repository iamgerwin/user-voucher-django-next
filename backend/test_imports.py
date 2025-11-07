#!/usr/bin/env python
"""
Simple test script to verify all imports work correctly.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

print("Testing imports...")
print("-" * 60)

# Test user imports
try:
    from apps.users.models import User
    from apps.users.serializers import (
        UserSerializer,
        UserCreateSerializer,
        UserListSerializer,
    )
    from apps.users.views import UserViewSet
    print("✓ User app imports successful")
except Exception as e:
    print(f"✗ User app imports failed: {e}")
    sys.exit(1)

# Test voucher imports
try:
    from apps.vouchers.models import (
        Voucher,
        PercentageDiscountVoucher,
        FixedAmountVoucher,
        FreeShippingVoucher,
        VoucherUsage,
    )
    from apps.vouchers.serializers import (
        VoucherSerializer,
        PercentageDiscountVoucherSerializer,
        FixedAmountVoucherSerializer,
        FreeShippingVoucherSerializer,
        VoucherUsageSerializer,
    )
    from apps.vouchers.views import (
        VoucherViewSet,
        PercentageDiscountVoucherViewSet,
        FixedAmountVoucherViewSet,
        FreeShippingVoucherViewSet,
        VoucherUsageViewSet,
    )
    print("✓ Voucher app imports successful")
except Exception as e:
    print(f"✗ Voucher app imports failed: {e}")
    sys.exit(1)

# Test URL imports
try:
    from django.urls import reverse
    from config.urls import urlpatterns
    print("✓ URL configuration imports successful")
except Exception as e:
    print(f"✗ URL imports failed: {e}")
    sys.exit(1)

# Test model creation (in memory)
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
    print("✓ Custom User model configured correctly")
except Exception as e:
    print(f"✗ User model configuration failed: {e}")
    sys.exit(1)

# Test serializer instantiation
try:
    serializer = UserSerializer()
    print("✓ UserSerializer can be instantiated")
except Exception as e:
    print(f"✗ UserSerializer instantiation failed: {e}")
    sys.exit(1)

try:
    serializer = VoucherSerializer()
    print("✓ VoucherSerializer can be instantiated")
except Exception as e:
    print(f"✗ VoucherSerializer instantiation failed: {e}")
    sys.exit(1)

print("-" * 60)
print("All import tests passed successfully!")
print("\nNext steps:")
print("1. Run: python manage.py makemigrations")
print("2. Run: python manage.py migrate")
print("3. Run: python manage.py createsuperuser")
print("4. Run: python manage.py runserver")
print("5. Visit: http://localhost:8000/api/docs/ for API documentation")
