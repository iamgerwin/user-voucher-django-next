"""
User model factory for testing.
"""

import factory
from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory

from apps.users.enums import UserRole, UserStatus

User = get_user_model()


class UserFactory(DjangoModelFactory):
    """
    Factory for creating User instances in tests.

    Usage:
        # Create a regular user
        user = UserFactory()

        # Create an admin user
        admin = UserFactory(role=UserRole.ADMIN, is_staff=True, is_superuser=True)

        # Create with custom email
        user = UserFactory(email='custom@example.com')
    """

    class Meta:
        model = User
        django_get_or_create = ('email',)

    email = factory.Sequence(lambda n: f'user{n}@example.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    phone_number = factory.Faker('phone_number')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')

    role = UserRole.USER
    status = UserStatus.ACTIVE
    is_active = True
    is_staff = False
    is_superuser = False

    @factory.post_generation
    def set_admin_fields(obj, create, extracted, **kwargs):
        """
        Automatically set is_staff and is_superuser if role is ADMIN.
        """
        if obj.role == UserRole.ADMIN and create:
            obj.is_staff = True
            obj.is_superuser = True
            obj.save()


class AdminUserFactory(UserFactory):
    """
    Factory for creating Admin users.

    Usage:
        admin = AdminUserFactory()
    """

    email = factory.Sequence(lambda n: f'admin{n}@example.com')
    role = UserRole.ADMIN
    is_staff = True
    is_superuser = True


class ManagerUserFactory(UserFactory):
    """
    Factory for creating Manager users.

    Usage:
        manager = ManagerUserFactory()
    """

    email = factory.Sequence(lambda n: f'manager{n}@example.com')
    role = UserRole.MANAGER


class InactiveUserFactory(UserFactory):
    """
    Factory for creating inactive users.

    Usage:
        inactive_user = InactiveUserFactory()
    """

    email = factory.Sequence(lambda n: f'inactive{n}@example.com')
    status = UserStatus.INACTIVE
    is_active = False
