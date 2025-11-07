"""
Voucher models with polymorphic relationships.

This module demonstrates polymorphic model inheritance using django-polymorphic.
We have a base Voucher model and specialized voucher types that inherit from it.
"""

from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from polymorphic.models import PolymorphicModel

from apps.core.models import TimeStampedModel
from apps.vouchers.enums import VoucherStatus, DiscountType


class Voucher(PolymorphicModel, TimeStampedModel):
    """
    Base voucher model using django-polymorphic for inheritance.

    This allows different voucher types to be queried together while
    maintaining their specific behavior and fields.

    Attributes:
        code: Unique voucher code
        name: Human-readable voucher name
        description: Detailed description of the voucher
        status: Current status of the voucher
        valid_from: Date when voucher becomes valid
        valid_until: Date when voucher expires
        usage_limit: Maximum number of times this voucher can be used (null = unlimited)
        usage_count: Current number of times voucher has been used
        created_by: User who created this voucher
    """

    code = models.CharField(
        _('code'),
        max_length=50,
        unique=True,
        db_index=True,
        help_text=_('Unique voucher code')
    )
    name = models.CharField(
        _('name'),
        max_length=200,
        help_text=_('Human-readable voucher name')
    )
    description = models.TextField(
        _('description'),
        blank=True,
        help_text=_('Detailed description of the voucher')
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=VoucherStatus.choices,
        default=VoucherStatus.ACTIVE,
        db_index=True,
        help_text=_('Current status of the voucher')
    )
    valid_from = models.DateTimeField(
        _('valid from'),
        default=timezone.now,
        help_text=_('Date when voucher becomes valid')
    )
    valid_until = models.DateTimeField(
        _('valid until'),
        help_text=_('Date when voucher expires')
    )
    usage_limit = models.PositiveIntegerField(
        _('usage limit'),
        null=True,
        blank=True,
        help_text=_('Maximum number of times this voucher can be used (null = unlimited)')
    )
    usage_count = models.PositiveIntegerField(
        _('usage count'),
        default=0,
        help_text=_('Current number of times voucher has been used')
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_vouchers',
        help_text=_('User who created this voucher')
    )

    class Meta:
        db_table = 'vouchers'
        verbose_name = _('voucher')
        verbose_name_plural = _('vouchers')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['code', 'status']),
            models.Index(fields=['status', 'valid_from', 'valid_until']),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"

    def clean(self):
        """
        Validate the voucher model instance.
        """
        super().clean()
        if self.valid_until and self.valid_from and self.valid_until <= self.valid_from:
            from django.core.exceptions import ValidationError
            raise ValidationError(_('Valid until date must be after valid from date'))

    @property
    def is_valid(self):
        """
        Check if voucher is currently valid.

        Returns:
            Boolean indicating if voucher is valid for use
        """
        now = timezone.now()
        return (
            self.status == VoucherStatus.ACTIVE and
            self.valid_from <= now <= self.valid_until and
            (self.usage_limit is None or self.usage_count < self.usage_limit)
        )

    @property
    def is_expired(self):
        """Check if voucher has expired."""
        return timezone.now() > self.valid_until

    def increment_usage(self):
        """
        Increment the usage count of the voucher.

        This method should be called when a voucher is successfully used.
        """
        self.usage_count += 1
        if self.usage_limit and self.usage_count >= self.usage_limit:
            self.status = VoucherStatus.USED
        self.save(update_fields=['usage_count', 'status', 'updated_at'])


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
        Voucher,
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
