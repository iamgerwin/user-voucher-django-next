"""
User account status enum.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class UserStatus(models.TextChoices):
    """
    User account status enum.
    """
    ACTIVE = 'ACTIVE', _('Active')
    INACTIVE = 'INACTIVE', _('Inactive')
    SUSPENDED = 'SUSPENDED', _('Suspended')
    PENDING = 'PENDING', _('Pending Verification')
