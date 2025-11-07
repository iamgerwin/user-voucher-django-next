"""
Tests for UserViewSet.
"""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

from apps.users.enums import UserRole, UserStatus
from apps.users.factories import UserFactory, AdminUserFactory, ManagerUserFactory

User = get_user_model()


@pytest.mark.django_db
class TestUserViewSetList:
    """Test suite for UserViewSet list action."""

    def test_list_users_as_admin(self, admin_client):
        """Test admin can list all users."""
        # Arrange
        UserFactory.create_batch(3)
        url = reverse('user-list')

        # Act
        response = admin_client.get(url)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 3

    def test_list_users_as_regular_user(self, authenticated_client, user):
        """Test regular users cannot list users (admin only)."""
        # Arrange
        UserFactory.create_batch(2, status=UserStatus.ACTIVE)
        from apps.users.factories import InactiveUserFactory
        InactiveUserFactory()
        url = reverse('user-list')

        # Act
        response = authenticated_client.get(url)

        # Assert
        # Based on viewset permissions, only admins can list users
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_users_unauthenticated(self, api_client):
        """Test unauthenticated users cannot list users."""
        # Arrange
        url = reverse('user-list')

        # Act
        response = api_client.get(url)

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestUserViewSetCreate:
    """Test suite for UserViewSet create action."""

    def test_create_user_unauthenticated(self, api_client):
        """Test anyone can register a new user."""
        # Arrange
        url = reverse('user-list')
        data = {
            'email': 'newuser@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
            'first_name': 'New',
            'last_name': 'User',
        }

        # Act
        response = api_client.post(url, data, format='json')

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['email'] == 'newuser@example.com'
        assert 'password' not in response.data

    def test_create_user_with_duplicate_email(self, api_client):
        """Test creating user with existing email fails."""
        # Arrange
        existing_user = UserFactory(email='existing@example.com')
        url = reverse('user-list')
        data = {
            'email': 'existing@example.com',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
            'first_name': 'Test',
            'last_name': 'User',
        }

        # Act
        response = api_client.post(url, data, format='json')

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUserViewSetRetrieve:
    """Test suite for UserViewSet retrieve action."""

    def test_retrieve_own_profile(self, authenticated_client, user):
        """Test user can retrieve their own profile."""
        # Arrange
        url = reverse('user-detail', kwargs={'pk': user.id})

        # Act
        response = authenticated_client.get(url)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == user.email

    def test_retrieve_other_user_as_regular_user(self, authenticated_client):
        """Test regular user cannot retrieve other user's profile."""
        # Arrange
        other_user = UserFactory()
        url = reverse('user-detail', kwargs={'pk': other_user.id})

        # Act
        response = authenticated_client.get(url)

        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_retrieve_other_user_as_admin(self, admin_client):
        """Test admin can retrieve any user's profile."""
        # Arrange
        other_user = UserFactory()
        url = reverse('user-detail', kwargs={'pk': other_user.id})

        # Act
        response = admin_client.get(url)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == other_user.email


@pytest.mark.django_db
class TestUserViewSetUpdate:
    """Test suite for UserViewSet update actions."""

    def test_update_own_profile(self, authenticated_client, user):
        """Test user can update their own profile."""
        # Arrange
        url = reverse('user-detail', kwargs={'pk': user.id})
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
        }

        # Act
        response = authenticated_client.patch(url, data, format='json')

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['first_name'] == 'Updated'
        assert response.data['last_name'] == 'Name'

    def test_update_other_user_as_regular_user(self, authenticated_client):
        """Test regular user cannot update other user's profile."""
        # Arrange
        other_user = UserFactory()
        url = reverse('user-detail', kwargs={'pk': other_user.id})
        data = {'first_name': 'Hacked'}

        # Act
        response = authenticated_client.patch(url, data, format='json')

        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_other_user_as_admin(self, admin_client):
        """Test admin can update any user's profile."""
        # Arrange
        other_user = UserFactory()
        url = reverse('user-detail', kwargs={'pk': other_user.id})
        data = {'first_name': 'AdminUpdated'}

        # Act
        response = admin_client.patch(url, data, format='json')

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['first_name'] == 'AdminUpdated'


@pytest.mark.django_db
class TestUserViewSetDelete:
    """Test suite for UserViewSet delete action."""

    def test_delete_user_as_admin(self, admin_client):
        """Test admin can delete users."""
        # Arrange
        user_to_delete = UserFactory()
        url = reverse('user-detail', kwargs={'pk': user_to_delete.id})

        # Act
        response = admin_client.delete(url)

        # Assert
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not User.objects.filter(id=user_to_delete.id).exists()

    def test_delete_user_as_regular_user(self, authenticated_client):
        """Test regular user cannot delete users."""
        # Arrange
        user_to_delete = UserFactory()
        url = reverse('user-detail', kwargs={'pk': user_to_delete.id})

        # Act
        response = authenticated_client.delete(url)

        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestUserViewSetCustomActions:
    """Test suite for UserViewSet custom actions."""

    def test_me_endpoint(self, authenticated_client, user):
        """Test /me endpoint returns current user."""
        # Arrange
        url = reverse('user-me')

        # Act
        response = authenticated_client.get(url)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == user.email

    def test_me_endpoint_unauthenticated(self, api_client):
        """Test /me endpoint requires authentication."""
        # Arrange
        url = reverse('user-me')

        # Act
        response = api_client.get(url)

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_change_password(self, authenticated_client, user):
        """Test password change endpoint."""
        # Arrange
        url = reverse('user-change-password')
        data = {
            'old_password': 'testpass123',
            'new_password': 'NewSecurePass123!',
            'new_password_confirm': 'NewSecurePass123!',
        }

        # Act
        response = authenticated_client.post(url, data, format='json')

        # Assert
        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.check_password('NewSecurePass123!') is True

    def test_change_password_wrong_old_password(self, authenticated_client):
        """Test password change fails with wrong old password."""
        # Arrange
        url = reverse('user-change-password')
        data = {
            'old_password': 'wrongpassword',
            'new_password': 'NewSecurePass123!',
            'new_password_confirm': 'NewSecurePass123!',
        }

        # Act
        response = authenticated_client.post(url, data, format='json')

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_activate_user_as_admin(self, admin_client):
        """Test admin can activate users."""
        # Arrange
        from apps.users.factories import InactiveUserFactory
        inactive_user = InactiveUserFactory()
        url = reverse('user-activate', kwargs={'pk': inactive_user.id})

        # Act
        response = admin_client.post(url)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        inactive_user.refresh_from_db()
        assert inactive_user.status == UserStatus.ACTIVE
        assert inactive_user.is_active is True

    def test_activate_user_as_regular_user(self, authenticated_client):
        """Test regular user cannot activate users."""
        # Arrange
        from apps.users.factories import InactiveUserFactory
        inactive_user = InactiveUserFactory()
        url = reverse('user-activate', kwargs={'pk': inactive_user.id})

        # Act
        response = authenticated_client.post(url)

        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_deactivate_user_as_admin(self, admin_client):
        """Test admin can deactivate users."""
        # Arrange
        active_user = UserFactory(status=UserStatus.ACTIVE)
        url = reverse('user-deactivate', kwargs={'pk': active_user.id})

        # Act
        response = admin_client.post(url)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        active_user.refresh_from_db()
        assert active_user.status == UserStatus.INACTIVE
        assert active_user.is_active is False

    def test_deactivate_superuser_fails(self, admin_client, admin_user):
        """Test cannot deactivate superuser accounts."""
        # Arrange
        superuser = AdminUserFactory(is_superuser=True)
        url = reverse('user-deactivate', kwargs={'pk': superuser.id})

        # Act
        response = admin_client.post(url)

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUserViewSetFiltering:
    """Test suite for UserViewSet filtering."""

    def test_filter_by_role(self, admin_client):
        """Test filtering users by role."""
        # Arrange
        AdminUserFactory.create_batch(2)
        ManagerUserFactory.create_batch(3)
        UserFactory.create_batch(4)
        url = reverse('user-list')

        # Act
        response = admin_client.get(url, {'role': UserRole.MANAGER})

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert all(
            user['role'] == UserRole.MANAGER
            for user in response.data['results']
        )

    def test_filter_by_status(self, admin_client):
        """Test filtering users by status."""
        # Arrange
        UserFactory.create_batch(3, status=UserStatus.ACTIVE)
        from apps.users.factories import InactiveUserFactory
        InactiveUserFactory.create_batch(2)
        url = reverse('user-list')

        # Act
        response = admin_client.get(url, {'status': UserStatus.INACTIVE})

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert all(
            user['status'] == UserStatus.INACTIVE
            for user in response.data['results']
        )

    def test_search_by_email(self, admin_client):
        """Test searching users by email."""
        # Arrange
        UserFactory(email='searchme@example.com')
        UserFactory(email='other@example.com')
        url = reverse('user-list')

        # Act
        response = admin_client.get(url, {'search': 'searchme'})

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1
        assert any(
            'searchme' in user['email']
            for user in response.data['results']
        )

    def test_ordering_by_email(self, admin_client):
        """Test ordering users by email."""
        # Arrange
        UserFactory(email='apple@example.com')
        UserFactory(email='zebra@example.com')
        UserFactory(email='banana@example.com')
        url = reverse('user-list')

        # Act
        response = admin_client.get(url, {'ordering': 'email'})

        # Assert
        assert response.status_code == status.HTTP_200_OK
        emails = [user['email'] for user in response.data['results']]
        assert emails == sorted(emails)
