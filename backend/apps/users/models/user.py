"""
User models with custom User model extending Django's AbstractBaseUser.
"""

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import EmailValidator, RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel
from apps.users.enums import UserRole, UserStatus
from apps.users.models.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    """
    Custom User model with email as the unique identifier.

    Attributes:
        email: User's email address (unique)
        first_name: User's first name
        last_name: User's last name
        phone_number: User's phone number (optional)
        role: User's role in the system
        status: User's account status
        is_staff: Whether user can access admin site
        is_active: Whether user account is active
    """

    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_('Phone number must be entered in the format: +999999999. Up to 15 digits allowed.')
    )

    email = models.EmailField(
        _('email address'),
        unique=True,
        db_index=True,
        validators=[EmailValidator()],
        help_text=_('Required. Valid email address.')
    )
    first_name = models.CharField(
        _('first name'),
        max_length=150,
        help_text=_('User\'s first name')
    )
    last_name = models.CharField(
        _('last name'),
        max_length=150,
        help_text=_('User\'s last name')
    )
    phone_number = models.CharField(
        _('phone number'),
        max_length=17,
        validators=[phone_regex],
        blank=True,
        null=True,
        help_text=_('User\'s contact phone number')
    )
    role = models.CharField(
        _('role'),
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.USER,
        db_index=True,
        help_text=_('User\'s role in the system')
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=UserStatus.choices,
        default=UserStatus.ACTIVE,
        db_index=True,
        help_text=_('User account status')
    )
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into the admin site.')
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_('Designates whether this user should be treated as active.')
    )
    date_joined = models.DateTimeField(
        _('date joined'),
        auto_now_add=True,
        help_text=_('Date when the user joined')
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        db_table = 'users'
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email', 'status']),
            models.Index(fields=['role', 'status']),
        ]

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    def get_full_name(self):
        """
        Return the user's full name.

        Returns:
            String with first_name and last_name
        """
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip() or self.email

    def get_short_name(self):
        """
        Return the user's short name (first name).

        Returns:
            String with first_name
        """
        return self.first_name or self.email

    def clean(self):
        """
        Validate the user model instance.
        """
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    @property
    def is_admin(self):
        """Check if user has admin role."""
        return self.role == UserRole.ADMIN

    @property
    def is_manager(self):
        """Check if user has manager role."""
        return self.role == UserRole.MANAGER
