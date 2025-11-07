"""
Custom manager for User model with email as the unique identifier.
"""

from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """
    Custom manager for User model with email as the unique identifier.
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a regular user with the given email and password.

        Args:
            email: User's email address
            password: User's password
            **extra_fields: Additional fields for the user

        Returns:
            User instance

        Raises:
            ValueError: If email is not provided
        """
        if not email:
            raise ValueError(_('The Email field must be set'))

        # Import here to avoid circular import
        from apps.users.enums import UserRole, UserStatus

        email = self.normalize_email(email)
        extra_fields.setdefault('role', UserRole.USER)
        extra_fields.setdefault('status', UserStatus.ACTIVE)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a superuser with the given email and password.

        Args:
            email: User's email address
            password: User's password
            **extra_fields: Additional fields for the user

        Returns:
            User instance
        """
        # Import here to avoid circular import
        from apps.users.enums import UserRole, UserStatus

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', UserRole.ADMIN)
        extra_fields.setdefault('status', UserStatus.ACTIVE)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)
