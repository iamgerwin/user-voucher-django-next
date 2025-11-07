"""
Voucher that provides a fixed amount discount.
"""

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.vouchers.models.base import Voucher


class FixedAmountVoucher(Voucher):
    """
    Voucher that provides a fixed amount discount.

    Attributes:
        discount_amount: Fixed amount to discount
        min_purchase_amount: Minimum purchase amount required to use voucher
    """

    discount_amount = models.DecimalField(
        _('discount amount'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text=_('Fixed amount to discount')
    )
    min_purchase_amount = models.DecimalField(
        _('minimum purchase amount'),
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text=_('Minimum purchase amount required to use voucher')
    )

    class Meta:
        verbose_name = _('fixed amount voucher')
        verbose_name_plural = _('fixed amount vouchers')

    def calculate_discount(self, purchase_amount):
        """
        Calculate the discount amount for a given purchase.

        Args:
            purchase_amount: The total purchase amount

        Returns:
            Decimal: The calculated discount amount
        """
        if purchase_amount < self.min_purchase_amount:
            return Decimal('0.00')

        return min(self.discount_amount, purchase_amount)
