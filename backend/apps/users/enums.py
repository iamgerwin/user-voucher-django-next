"""
Enums for the users app to avoid magic strings and numbers.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class UserRole(models.TextChoices):
    """
    User role enum for role-based access control.
    """
    ADMIN = 'ADMIN', _('Administrator')
    MANAGER = 'MANAGER', _('Manager')
    USER = 'USER', _('Regular User')
    GUEST = 'GUEST', _('Guest')


class UserStatus(models.TextChoices):
    """
    User account status enum.
    """
    ACTIVE = 'ACTIVE', _('Active')
    INACTIVE = 'INACTIVE', _('Inactive')
    SUSPENDED = 'SUSPENDED', _('Suspended')
    PENDING = 'PENDING', _('Pending Verification')
