"""
Core permissions package.
"""

from apps.core.permissions.base import IsAdminOrReadOnly, IsOwnerOrAdmin

__all__ = ['IsAdminOrReadOnly', 'IsOwnerOrAdmin']
