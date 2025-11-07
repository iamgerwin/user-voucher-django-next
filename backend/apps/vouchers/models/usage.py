"""
Track voucher usage by users.
"""

from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel


class VoucherUsage(TimeStampedModel):
    """
    Track voucher usage by users.

    This model maintains a many-to-many relationship between users and vouchers,
    tracking when and by whom a voucher was used.

    Attributes:
        voucher: The voucher that was used
        user: The user who used the voucher
        purchase_amount: The purchase amount when voucher was used
        discount_applied: The actual discount amount applied
        used_at: Timestamp when voucher was used
    """

    voucher = models.ForeignKey(
        'vouchers.Voucher',
        on_delete=models.CASCADE,
        related_name='usages',
        help_text=_('The voucher that was used')
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='voucher_usages',
        help_text=_('The user who used the voucher')
    )
    purchase_amount = models.DecimalField(
        _('purchase amount'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text=_('The purchase amount when voucher was used')
    )
    discount_applied = models.DecimalField(
        _('discount applied'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text=_('The actual discount amount applied')
    )
    used_at = models.DateTimeField(
        _('used at'),
        auto_now_add=True,
        db_index=True,
        help_text=_('Timestamp when voucher was used')
    )

    class Meta:
        db_table = 'voucher_usages'
        verbose_name = _('voucher usage')
        verbose_name_plural = _('voucher usages')
        ordering = ['-used_at']
        indexes = [
            models.Index(fields=['voucher', 'user']),
            models.Index(fields=['user', 'used_at']),
        ]

    def __str__(self):
        return f"{self.user.email} used {self.voucher.code} on {self.used_at}"
