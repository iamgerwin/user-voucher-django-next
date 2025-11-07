"""
Tests for Voucher serializers.
"""

from decimal import Decimal

import pytest
from django.utils import timezone

from apps.vouchers.serializers import VoucherSerializer, VoucherListSerializer
from apps.vouchers.factories import (
    PercentageDiscountVoucherFactory,
    FixedAmountVoucherFactory,
    FreeShippingVoucherFactory
)
from apps.vouchers.enums import VoucherStatus
from apps.users.factories import UserFactory


@pytest.mark.django_db
class TestVoucherSerializer:
    """Test suite for VoucherSerializer."""

    def test_serialize_percentage_voucher(self):
        """Test serializing a percentage discount voucher."""
        # Arrange
        voucher = PercentageDiscountVoucherFactory()

        # Act
        serializer = VoucherSerializer(voucher)
        data = serializer.data

        # Assert
        assert data['id'] == voucher.id
        assert data['code'] == voucher.code
        assert data['name'] == voucher.name
        assert data['status'] == voucher.status
        assert data['voucher_type'] == 'percentagediscountvoucher'
        assert 'is_valid' in data
        assert 'is_expired' in data

    def test_serialize_fixed_amount_voucher(self):
        """Test serializing a fixed amount voucher."""
        # Arrange
        voucher = FixedAmountVoucherFactory()

        # Act
        serializer = VoucherSerializer(voucher)
        data = serializer.data

        # Assert
        assert data['voucher_type'] == 'fixedamountvoucher'

    def test_serialize_free_shipping_voucher(self):
        """Test serializing a free shipping voucher."""
        # Arrange
        voucher = FreeShippingVoucherFactory()

        # Act
        serializer = VoucherSerializer(voucher)
        data = serializer.data

        # Assert
        assert data['voucher_type'] == 'freeshippingvoucher'

    def test_created_by_name_field(self):
        """Test created_by_name field shows creator's full name."""
        # Arrange
        user = UserFactory(first_name='John', last_name='Doe')
        voucher = PercentageDiscountVoucherFactory(created_by=user)

        # Act
        serializer = VoucherSerializer(voucher)

        # Assert
        assert serializer.data['created_by_name'] == 'John Doe'

    def test_usage_percentage_with_limit(self):
        """Test usage_percentage calculation with usage limit."""
        # Arrange
        voucher = PercentageDiscountVoucherFactory(
            usage_limit=100,
            usage_count=25
        )

        # Act
        serializer = VoucherSerializer(voucher)

        # Assert
        assert serializer.data['usage_percentage'] == 25.0

    def test_usage_percentage_without_limit(self):
        """Test usage_percentage is None without usage limit."""
        # Arrange
        voucher = PercentageDiscountVoucherFactory(
            usage_limit=None,
            usage_count=100
        )

        # Act
        serializer = VoucherSerializer(voucher)

        # Assert
        assert serializer.data['usage_percentage'] is None

    def test_validate_code_uppercase_conversion(self):
        """Test voucher code is converted to uppercase."""
        # Arrange
        user = UserFactory()
        data = {
            'code': 'test123',
            'name': 'Test Voucher',
            'status': VoucherStatus.ACTIVE,
            'valid_from': timezone.now(),
            'valid_until': timezone.now() + timezone.timedelta(days=30),
            'created_by': user.id,
        }

        # Act
        serializer = VoucherSerializer(data=data)

        # Assert
        assert serializer.is_valid()
        assert serializer.validated_data['code'] == 'TEST123'

    def test_validate_duplicate_code_on_create(self):
        """Test validation fails when creating voucher with duplicate code."""
        # Arrange
        existing = PercentageDiscountVoucherFactory(code='DUPLICATE')
        user = UserFactory()
        data = {
            'code': 'DUPLICATE',
            'name': 'Test Voucher',
            'status': VoucherStatus.ACTIVE,
            'valid_from': timezone.now(),
            'valid_until': timezone.now() + timezone.timedelta(days=30),
            'created_by': user.id,
        }

        # Act
        serializer = VoucherSerializer(data=data)

        # Assert
        assert not serializer.is_valid()
        assert 'code' in serializer.errors

    def test_validate_dates(self):
        """Test validation fails when valid_until <= valid_from."""
        # Arrange
        now = timezone.now()
        user = UserFactory()
        data = {
            'code': 'TEST123',
            'name': 'Test Voucher',
            'status': VoucherStatus.ACTIVE,
            'valid_from': now + timezone.timedelta(days=10),
            'valid_until': now + timezone.timedelta(days=5),
            'created_by': user.id,
        }

        # Act
        serializer = VoucherSerializer(data=data)

        # Assert
        assert not serializer.is_valid()
        assert 'valid_until' in serializer.errors

    def test_read_only_fields(self):
        """Test read-only fields cannot be modified."""
        # Arrange
        voucher = PercentageDiscountVoucherFactory(usage_count=5)
        original_count = voucher.usage_count

        # Act
        serializer = VoucherSerializer(
            voucher,
            data={'usage_count': 100},
            partial=True
        )

        # Assert
        assert serializer.is_valid()
        serializer.save()
        voucher.refresh_from_db()
        assert voucher.usage_count == original_count


@pytest.mark.django_db
class TestVoucherListSerializer:
    """Test suite for VoucherListSerializer."""

    def test_serialize_voucher_list(self):
        """Test serializing vouchers with minimal fields."""
        # Arrange
        voucher = PercentageDiscountVoucherFactory()

        # Act
        serializer = VoucherListSerializer(voucher)
        data = serializer.data

        # Assert
        assert 'id' in data
        assert 'code' in data
        assert 'name' in data
        assert 'status' in data
        assert 'voucher_type' in data
        assert 'is_valid' in data
        # Should not include detailed fields
        assert 'description' not in data
        assert 'created_by' not in data

    def test_all_fields_are_read_only(self):
        """Test all fields in list serializer are read-only."""
        # Arrange
        voucher = PercentageDiscountVoucherFactory()

        # Act
        serializer = VoucherListSerializer(voucher)

        # Assert
        assert serializer.Meta.read_only_fields == serializer.Meta.fields

    def test_voucher_type_field(self):
        """Test voucher_type field correctly identifies voucher types."""
        # Arrange
        percentage = PercentageDiscountVoucherFactory()
        fixed = FixedAmountVoucherFactory()
        free_shipping = FreeShippingVoucherFactory()

        # Act
        percentage_data = VoucherListSerializer(percentage).data
        fixed_data = VoucherListSerializer(fixed).data
        free_shipping_data = VoucherListSerializer(free_shipping).data

        # Assert
        assert percentage_data['voucher_type'] == 'percentagediscountvoucher'
        assert fixed_data['voucher_type'] == 'fixedamountvoucher'
        assert free_shipping_data['voucher_type'] == 'freeshippingvoucher'


@pytest.mark.django_db
class TestPercentageDiscountVoucherSerializer:
    """Test suite for PercentageDiscountVoucher serializer."""

    def test_serialize_percentage_voucher_specific_fields(self):
        """Test serializing percentage voucher includes specific fields."""
        # Arrange
        from apps.vouchers.serializers import PercentageDiscountVoucherSerializer
        voucher = PercentageDiscountVoucherFactory(
            discount_percentage=Decimal('15.00'),
            max_discount_amount=Decimal('50.00'),
            min_purchase_amount=Decimal('100.00')
        )

        # Act
        serializer = PercentageDiscountVoucherSerializer(voucher)
        data = serializer.data

        # Assert
        assert str(data['discount_percentage']) == '15.00'
        assert str(data['max_discount_amount']) == '50.00'
        assert str(data['min_purchase_amount']) == '100.00'


@pytest.mark.django_db
class TestFixedAmountVoucherSerializer:
    """Test suite for FixedAmountVoucher serializer."""

    def test_serialize_fixed_voucher_specific_fields(self):
        """Test serializing fixed amount voucher includes specific fields."""
        # Arrange
        from apps.vouchers.serializers import FixedAmountVoucherSerializer
        voucher = FixedAmountVoucherFactory(
            discount_amount=Decimal('25.00'),
            min_purchase_amount=Decimal('100.00')
        )

        # Act
        serializer = FixedAmountVoucherSerializer(voucher)
        data = serializer.data

        # Assert
        assert str(data['discount_amount']) == '25.00'
        assert str(data['min_purchase_amount']) == '100.00'


@pytest.mark.django_db
class TestFreeShippingVoucherSerializer:
    """Test suite for FreeShippingVoucher serializer."""

    def test_serialize_free_shipping_voucher_specific_fields(self):
        """Test serializing free shipping voucher includes specific fields."""
        # Arrange
        from apps.vouchers.serializers import FreeShippingVoucherSerializer
        voucher = FreeShippingVoucherFactory(
            min_purchase_amount=Decimal('50.00'),
            max_shipping_amount=Decimal('15.00')
        )

        # Act
        serializer = FreeShippingVoucherSerializer(voucher)
        data = serializer.data

        # Assert
        assert str(data['min_purchase_amount']) == '50.00'
        assert str(data['max_shipping_amount']) == '15.00'


@pytest.mark.django_db
class TestVoucherUsageSerializer:
    """Test suite for VoucherUsageSerializer."""

    def test_serialize_voucher_usage(self):
        """Test serializing a voucher usage record."""
        # Arrange
        from apps.vouchers.serializers import VoucherUsageSerializer
        from apps.vouchers.factories import VoucherUsageFactory
        usage = VoucherUsageFactory(
            purchase_amount=Decimal('100.00'),
            discount_applied=Decimal('10.00')
        )

        # Act
        serializer = VoucherUsageSerializer(usage)
        data = serializer.data

        # Assert
        assert data['id'] == usage.id
        assert str(data['purchase_amount']) == '100.00'
        assert str(data['discount_applied']) == '10.00'
        assert 'voucher' in data
        assert 'user' in data
        assert 'used_at' in data
