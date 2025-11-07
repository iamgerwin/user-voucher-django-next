"""
ViewSet specifically for fixed amount vouchers.
"""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from apps.vouchers.models import FixedAmountVoucher
from apps.vouchers.serializers import FixedAmountVoucherSerializer


class FixedAmountVoucherViewSet(viewsets.ModelViewSet):
    """
    ViewSet specifically for fixed amount vouchers.
    """
    queryset = FixedAmountVoucher.objects.all()
    serializer_class = FixedAmountVoucherSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['code', 'name']
    ordering_fields = ['created_at', 'discount_amount']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Optimize queryset.
        """
        return super().get_queryset().select_related('created_by')

    def get_permissions(self):
        """
        Set permissions based on action.
        """
        if self.action in ['create', 'update', 'partial_update']:
            permission_classes = [IsAuthenticated]
        elif self.action == 'destroy':
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """
        Save voucher with created_by.
        """
        if not (self.request.user.is_admin or self.request.user.is_manager):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only admins and managers can create vouchers.")

        serializer.save(created_by=self.request.user)
