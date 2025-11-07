"""
Voucher that provides a percentage discount.
"""

from decimal import Decimal

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.vouchers.models.base import Voucher


class PercentageDiscountVoucher(Voucher):
    """
    Voucher that provides a percentage discount.

    Attributes:
        discount_percentage: Percentage to discount (0-100)
        max_discount_amount: Maximum discount amount (optional cap)
        min_purchase_amount: Minimum purchase amount required to use voucher
    """

    discount_percentage = models.DecimalField(
        _('discount percentage'),
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01')), MaxValueValidator(Decimal('100.00'))],
        help_text=_('Percentage to discount (0-100)')
    )
    max_discount_amount = models.DecimalField(
        _('maximum discount amount'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text=_('Maximum discount amount (optional cap)')
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
        verbose_name = _('percentage discount voucher')
        verbose_name_plural = _('percentage discount vouchers')

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

        discount = purchase_amount * (self.discount_percentage / Decimal('100'))

        if self.max_discount_amount:
            discount = min(discount, self.max_discount_amount)

        return discount.quantize(Decimal('0.01'))
