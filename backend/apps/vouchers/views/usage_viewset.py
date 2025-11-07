"""
ViewSet for viewing voucher usage records.
"""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated

from apps.vouchers.models import VoucherUsage
from apps.vouchers.serializers import VoucherUsageSerializer


class VoucherUsageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing voucher usage records.

    Read-only viewset as usage creation is handled through voucher endpoints.
    """
    queryset = VoucherUsage.objects.all()
    serializer_class = VoucherUsageSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['voucher', 'user']
    ordering_fields = ['used_at', 'purchase_amount', 'discount_applied']
    ordering = ['-used_at']
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Optimize queryset and filter based on user permissions.
        """
        queryset = super().get_queryset().select_related('voucher', 'user')

        # Admins can see all usage records
        if self.request.user.is_admin:
            return queryset

        # Regular users can only see their own usage records
        return queryset.filter(user=self.request.user)
