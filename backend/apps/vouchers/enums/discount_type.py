"""
Discount type enum for vouchers.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class DiscountType(models.TextChoices):
    """
    Discount type enum for vouchers.
    """
    PERCENTAGE = 'PERCENTAGE', _('Percentage Discount')
    FIXED_AMOUNT = 'FIXED_AMOUNT', _('Fixed Amount Discount')
    FREE_SHIPPING = 'FREE_SHIPPING', _('Free Shipping')
