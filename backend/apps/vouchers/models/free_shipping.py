"""
Voucher that provides free shipping.
"""

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.vouchers.models.base import Voucher


class FreeShippingVoucher(Voucher):
    """
    Voucher that provides free shipping.

    Attributes:
        min_purchase_amount: Minimum purchase amount required to use voucher
        max_shipping_amount: Maximum shipping amount that will be covered
    """

    min_purchase_amount = models.DecimalField(
        _('minimum purchase amount'),
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text=_('Minimum purchase amount required to use voucher')
    )
    max_shipping_amount = models.DecimalField(
        _('maximum shipping amount'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text=_('Maximum shipping amount that will be covered')
    )

    class Meta:
        verbose_name = _('free shipping voucher')
        verbose_name_plural = _('free shipping vouchers')

    def calculate_discount(self, purchase_amount, shipping_amount):
        """
        Calculate the shipping discount for a given purchase.

        Args:
            purchase_amount: The total purchase amount
            shipping_amount: The shipping cost

        Returns:
            Decimal: The calculated shipping discount
        """
        if purchase_amount < self.min_purchase_amount:
            return Decimal('0.00')

        if self.max_shipping_amount:
            return min(shipping_amount, self.max_shipping_amount)

        return shipping_amount
