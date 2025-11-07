"""
Voucher status enum.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class VoucherStatus(models.TextChoices):
    """
    Voucher status enum.
    """
    ACTIVE = 'ACTIVE', _('Active')
    EXPIRED = 'EXPIRED', _('Expired')
    USED = 'USED', _('Used')
    CANCELLED = 'CANCELLED', _('Cancelled')
