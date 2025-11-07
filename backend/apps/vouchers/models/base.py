"""
Base voucher model using django-polymorphic for inheritance.
"""

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from polymorphic.models import PolymorphicModel

from apps.core.models import TimeStampedModel
from apps.vouchers.enums import VoucherStatus


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
