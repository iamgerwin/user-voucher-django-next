"""
User role enum for role-based access control.
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
