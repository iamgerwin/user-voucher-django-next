"""
Enums for the vouchers app to avoid magic strings and numbers.
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


class DiscountType(models.TextChoices):
    """
    Discount type enum for vouchers.
    """
    PERCENTAGE = 'PERCENTAGE', _('Percentage Discount')
    FIXED_AMOUNT = 'FIXED_AMOUNT', _('Fixed Amount Discount')
    FREE_SHIPPING = 'FREE_SHIPPING', _('Free Shipping')
