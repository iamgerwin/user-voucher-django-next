"""
Tests for VoucherViewSet.
"""

from decimal import Decimal

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from apps.vouchers.enums import VoucherStatus
from apps.vouchers.factories import (
    PercentageDiscountVoucherFactory,
    FixedAmountVoucherFactory,
    FreeShippingVoucherFactory,
)
from apps.users.factories import UserFactory, AdminUserFactory, ManagerUserFactory


@pytest.mark.django_db
class TestVoucherViewSetList:
    """Test suite for VoucherViewSet list action."""

    def test_list_vouchers_as_admin(self, admin_client):
        """Test admin can list all vouchers."""
        # Arrange
        PercentageDiscountVoucherFactory.create_batch(2)
        FixedAmountVoucherFactory.create_batch(2)
        url = reverse('voucher-list')

        # Act
        response = admin_client.get(url)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 4

    def test_list_vouchers_as_manager(self, api_client):
        """Test manager can list all vouchers."""
        # Arrange
        manager = ManagerUserFactory()
        api_client.force_authenticate(user=manager)
        PercentageDiscountVoucherFactory.create_batch(3)
        url = reverse('voucher-list')

        # Act
        response = api_client.get(url)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 3

    def test_list_vouchers_as_regular_user(self, authenticated_client):
        """Test regular users can only see active vouchers."""
        # Arrange
        PercentageDiscountVoucherFactory.create_batch(2, status=VoucherStatus.ACTIVE)
        PercentageDiscountVoucherFactory.create_batch(2, status=VoucherStatus.EXPIRED)
        url = reverse('voucher-list')

        # Act
        response = authenticated_client.get(url)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        # Should only see active vouchers
        for result in response.data['results']:
            assert result['status'] == VoucherStatus.ACTIVE

    def test_list_vouchers_unauthenticated(self, api_client):
        """Test unauthenticated users cannot list vouchers."""
        # Arrange
        url = reverse('voucher-list')

        # Act
        response = api_client.get(url)

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestVoucherViewSetRetrieve:
    """Test suite for VoucherViewSet retrieve action."""

    def test_retrieve_voucher_as_admin(self, admin_client):
        """Test admin can retrieve any voucher."""
        # Arrange
        voucher = PercentageDiscountVoucherFactory()
        url = reverse('voucher-detail', kwargs={'pk': voucher.id})

        # Act
        response = admin_client.get(url)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == voucher.code

    def test_retrieve_active_voucher_as_user(self, authenticated_client):
        """Test user can retrieve active voucher."""
        # Arrange
        voucher = PercentageDiscountVoucherFactory(status=VoucherStatus.ACTIVE)
        url = reverse('voucher-detail', kwargs={'pk': voucher.id})

        # Act
        response = authenticated_client.get(url)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == voucher.code

    def test_retrieve_expired_voucher_as_user_fails(self, authenticated_client):
        """Test user cannot retrieve expired voucher."""
        # Arrange
        voucher = PercentageDiscountVoucherFactory(status=VoucherStatus.EXPIRED)
        url = reverse('voucher-detail', kwargs={'pk': voucher.id})

        # Act
        response = authenticated_client.get(url)

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestVoucherViewSetCreate:
    """Test suite for VoucherViewSet create action."""

    def test_create_percentage_voucher_as_admin(self, admin_client, admin_user):
        """Test admin can create percentage voucher."""
        # Arrange
        url = reverse('voucher-list')
        data = {
            'voucher_type': 'percentagediscountvoucher',
            'code': 'NEWVOUCHER',
            'name': 'New Voucher',
            'status': VoucherStatus.ACTIVE,
            'valid_from': timezone.now().isoformat(),
            'valid_until': (timezone.now() + timezone.timedelta(days=30)).isoformat(),
            'discount_percentage': '15.00',
            'min_purchase_amount': '0.00',
        }

        # Act
        response = admin_client.post(url, data, format='json')

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['code'] == 'NEWVOUCHER'

    def test_create_fixed_voucher_as_manager(self, api_client):
        """Test manager can create fixed amount voucher."""
        # Arrange
        manager = ManagerUserFactory()
        api_client.force_authenticate(user=manager)
        url = reverse('voucher-list')
        data = {
            'voucher_type': 'fixedamountvoucher',
            'code': 'FIXED50',
            'name': 'Fixed $50 Off',
            'status': VoucherStatus.ACTIVE,
            'valid_from': timezone.now().isoformat(),
            'valid_until': (timezone.now() + timezone.timedelta(days=30)).isoformat(),
            'discount_amount': '50.00',
            'min_purchase_amount': '100.00',
        }

        # Act
        response = api_client.post(url, data, format='json')

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['code'] == 'FIXED50'

    def test_create_voucher_as_regular_user_fails(self, authenticated_client):
        """Test regular user cannot create vouchers."""
        # Arrange
        url = reverse('voucher-list')
        data = {
            'voucher_type': 'percentagediscountvoucher',
            'code': 'TESTCODE',
            'name': 'Test',
            'status': VoucherStatus.ACTIVE,
            'valid_from': timezone.now().isoformat(),
            'valid_until': (timezone.now() + timezone.timedelta(days=30)).isoformat(),
            'discount_percentage': '10.00',
        }

        # Act
        response = authenticated_client.post(url, data, format='json')

        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestVoucherViewSetUpdate:
    """Test suite for VoucherViewSet update actions."""

    def test_update_voucher_as_admin(self, admin_client):
        """Test admin can update vouchers."""
        # Arrange
        voucher = PercentageDiscountVoucherFactory()
        url = reverse('voucher-detail', kwargs={'pk': voucher.id})
        data = {
            'name': 'Updated Name',
            'description': 'Updated description',
        }

        # Act
        response = admin_client.patch(url, data, format='json')

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Updated Name'

    def test_update_voucher_as_manager(self, api_client):
        """Test manager can update vouchers."""
        # Arrange
        manager = ManagerUserFactory()
        api_client.force_authenticate(user=manager)
        voucher = PercentageDiscountVoucherFactory()
        url = reverse('voucher-detail', kwargs={'pk': voucher.id})
        data = {'name': 'Manager Updated'}

        # Act
        response = api_client.patch(url, data, format='json')

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Manager Updated'

    def test_update_voucher_as_regular_user_fails(self, authenticated_client):
        """Test regular user cannot update vouchers."""
        # Arrange
        voucher = PercentageDiscountVoucherFactory()
        url = reverse('voucher-detail', kwargs={'pk': voucher.id})
        data = {'name': 'Hacked'}

        # Act
        response = authenticated_client.patch(url, data, format='json')

        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestVoucherViewSetDelete:
    """Test suite for VoucherViewSet delete action."""

    def test_delete_voucher_as_admin(self, admin_client):
        """Test admin can delete vouchers."""
        # Arrange
        voucher = PercentageDiscountVoucherFactory()
        url = reverse('voucher-detail', kwargs={'pk': voucher.id})

        # Act
        response = admin_client.delete(url)

        # Assert
        assert response.status_code == status.HTTP_204_NO_CONTENT
        from apps.vouchers.models import Voucher
        assert not Voucher.objects.filter(id=voucher.id).exists()

    def test_delete_voucher_as_manager_fails(self, api_client):
        """Test manager cannot delete vouchers."""
        # Arrange
        manager = ManagerUserFactory()
        api_client.force_authenticate(user=manager)
        voucher = PercentageDiscountVoucherFactory()
        url = reverse('voucher-detail', kwargs={'pk': voucher.id})

        # Act
        response = api_client.delete(url)

        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_voucher_as_regular_user_fails(self, authenticated_client):
        """Test regular user cannot delete vouchers."""
        # Arrange
        voucher = PercentageDiscountVoucherFactory()
        url = reverse('voucher-detail', kwargs={'pk': voucher.id})

        # Act
        response = authenticated_client.delete(url)

        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestVoucherViewSetFiltering:
    """Test suite for VoucherViewSet filtering."""

    def test_filter_by_status(self, admin_client):
        """Test filtering vouchers by status."""
        # Arrange
        PercentageDiscountVoucherFactory.create_batch(2, status=VoucherStatus.ACTIVE)
        PercentageDiscountVoucherFactory.create_batch(2, status=VoucherStatus.EXPIRED)
        url = reverse('voucher-list')

        # Act
        response = admin_client.get(url, {'status': VoucherStatus.EXPIRED})

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert all(
            voucher['status'] == VoucherStatus.EXPIRED
            for voucher in response.data['results']
        )

    def test_search_by_code(self, admin_client):
        """Test searching vouchers by code."""
        # Arrange
        PercentageDiscountVoucherFactory(code='SEARCHME')
        PercentageDiscountVoucherFactory(code='OTHER123')
        url = reverse('voucher-list')

        # Act
        response = admin_client.get(url, {'search': 'SEARCHME'})

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1
        assert any(
            'SEARCHME' in voucher['code']
            for voucher in response.data['results']
        )

    def test_ordering_by_created_at(self, admin_client):
        """Test ordering vouchers by created_at."""
        # Arrange
        voucher1 = PercentageDiscountVoucherFactory()
        voucher2 = PercentageDiscountVoucherFactory()
        voucher3 = PercentageDiscountVoucherFactory()
        url = reverse('voucher-list')

        # Act
        response = admin_client.get(url, {'ordering': 'created_at'})

        # Assert
        assert response.status_code == status.HTTP_200_OK
        # Should be in ascending order
        ids = [v['id'] for v in response.data['results']]
        assert ids[0] == voucher1.id


@pytest.mark.django_db
class TestVoucherViewSetPolymorphism:
    """Test suite for polymorphic voucher handling."""

    def test_retrieve_returns_correct_voucher_type(self, admin_client):
        """Test retrieve returns correct polymorphic type."""
        # Arrange
        percentage = PercentageDiscountVoucherFactory()
        fixed = FixedAmountVoucherFactory()
        free_shipping = FreeShippingVoucherFactory()

        # Act
        percentage_response = admin_client.get(
            reverse('voucher-detail', kwargs={'pk': percentage.id})
        )
        fixed_response = admin_client.get(
            reverse('voucher-detail', kwargs={'pk': fixed.id})
        )
        free_shipping_response = admin_client.get(
            reverse('voucher-detail', kwargs={'pk': free_shipping.id})
        )

        # Assert
        assert percentage_response.status_code == status.HTTP_200_OK
        assert percentage_response.data['voucher_type'] == 'percentagediscountvoucher'
        # Note: The viewset should return the base serializer unless specifically configured
        # If you need type-specific fields, retrieve would need to use type-specific serializers

        assert fixed_response.status_code == status.HTTP_200_OK
        assert fixed_response.data['voucher_type'] == 'fixedamountvoucher'

        assert free_shipping_response.status_code == status.HTTP_200_OK
        assert free_shipping_response.data['voucher_type'] == 'freeshippingvoucher'

    def test_list_includes_all_voucher_types(self, admin_client):
        """Test list endpoint includes all voucher types."""
        # Arrange
        PercentageDiscountVoucherFactory()
        FixedAmountVoucherFactory()
        FreeShippingVoucherFactory()
        url = reverse('voucher-list')

        # Act
        response = admin_client.get(url)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        voucher_types = {v['voucher_type'] for v in response.data['results']}
        assert 'percentagediscountvoucher' in voucher_types
        assert 'fixedamountvoucher' in voucher_types
        assert 'freeshippingvoucher' in voucher_types
