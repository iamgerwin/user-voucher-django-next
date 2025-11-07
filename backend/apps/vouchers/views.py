"""
Voucher viewsets for REST API with polymorphic support.
"""

from django.db.models import Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from apps.vouchers.enums import VoucherStatus
from apps.vouchers.models import (
    Voucher,
    PercentageDiscountVoucher,
    FixedAmountVoucher,
    FreeShippingVoucher,
    VoucherUsage,
)
from apps.vouchers.serializers import (
    VoucherSerializer,
    PercentageDiscountVoucherSerializer,
    FixedAmountVoucherSerializer,
    FreeShippingVoucherSerializer,
    VoucherListSerializer,
    VoucherUsageSerializer,
    VoucherUsageCreateSerializer,
    VoucherValidateSerializer,
)


class VoucherViewSet(viewsets.ModelViewSet):
    """
    ViewSet for polymorphic Voucher models with proper optimizations.

    Endpoints:
    - list: Get all vouchers
    - retrieve: Get specific voucher
    - create: Create new voucher (admin/manager only)
    - update: Update voucher (admin/manager only)
    - partial_update: Partially update voucher
    - destroy: Delete voucher (admin only)
    - validate: Validate voucher code and calculate discount
    - usages: Get usage history for a voucher
    - use_voucher: Record voucher usage
    """
    queryset = Voucher.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'polymorphic_ctype']
    search_fields = ['code', 'name', 'description']
    ordering_fields = ['created_at', 'valid_from', 'valid_until', 'usage_count']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Optimize queryset with select_related and prefetch_related.
        """
        queryset = super().get_queryset()

        # Always select related created_by to prevent N+1 queries
        queryset = queryset.select_related('created_by', 'polymorphic_ctype')

        # Filter based on user role
        if self.request.user.is_authenticated:
            if self.request.user.is_admin or self.request.user.is_manager:
                # Admins and managers can see all vouchers
                return queryset
            else:
                # Regular users can only see active, valid vouchers
                return queryset.filter(status=VoucherStatus.ACTIVE)
        else:
            # Anonymous users can't access vouchers
            return queryset.none()

    def get_serializer_class(self):
        """
        Return appropriate serializer based on action and voucher type.
        """
        if self.action == 'list':
            return VoucherListSerializer
        elif self.action == 'validate':
            return VoucherValidateSerializer

        # For detail/create/update, use specific serializer based on type
        if self.action in ['create', 'update', 'partial_update']:
            voucher_type = None

            # Get type from request data for create
            if self.action == 'create':
                voucher_type = self.request.data.get('voucher_type')
            # Get type from instance for update
            elif hasattr(self, 'get_object'):
                try:
                    obj = self.get_object()
                    voucher_type = obj.polymorphic_ctype.model
                except:
                    pass

            # Return appropriate serializer
            if voucher_type == 'percentagediscountvoucher':
                return PercentageDiscountVoucherSerializer
            elif voucher_type == 'fixedamountvoucher':
                return FixedAmountVoucherSerializer
            elif voucher_type == 'freeshippingvoucher':
                return FreeShippingVoucherSerializer

        # Default serializer
        return VoucherSerializer

    def get_permissions(self):
        """
        Set permissions based on action.
        """
        if self.action in ['create', 'update', 'partial_update']:
            # Only admins and managers can create/update vouchers
            permission_classes = [IsAuthenticated]
        elif self.action == 'destroy':
            # Only admins can delete vouchers
            permission_classes = [IsAdminUser]
        else:
            # Everyone authenticated can read
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """
        Save voucher with created_by set to current user.
        """
        # Check if user has permission to create vouchers
        if not (self.request.user.is_admin or self.request.user.is_manager):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only admins and managers can create vouchers.")

        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        """
        Update voucher with permission check.
        """
        # Check if user has permission to update vouchers
        if not (self.request.user.is_admin or self.request.user.is_manager):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only admins and managers can update vouchers.")

        serializer.save()

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def validate(self, request):
        """
        Validate a voucher code and calculate discount.

        POST /api/vouchers/validate/
        Body: {
            "code": "VOUCHER_CODE",
            "purchase_amount": "100.00",
            "shipping_amount": "10.00"  // Optional, for free shipping vouchers
        }
        """
        serializer = VoucherValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        voucher = serializer.validated_data['voucher']
        calculated_discount = serializer.validated_data['calculated_discount']

        # Use polymorphic serializer for voucher
        if isinstance(voucher, PercentageDiscountVoucher):
            voucher_serializer = PercentageDiscountVoucherSerializer(voucher)
        elif isinstance(voucher, FixedAmountVoucher):
            voucher_serializer = FixedAmountVoucherSerializer(voucher)
        elif isinstance(voucher, FreeShippingVoucher):
            voucher_serializer = FreeShippingVoucherSerializer(voucher)
        else:
            voucher_serializer = VoucherSerializer(voucher)

        return Response({
            'valid': True,
            'voucher': voucher_serializer.data,
            'calculated_discount': str(calculated_discount),
        })

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def usages(self, request, pk=None):
        """
        Get usage history for a specific voucher.

        GET /api/vouchers/{id}/usages/
        """
        voucher = self.get_object()

        # Only admins/managers and voucher creator can see usage history
        if not (request.user.is_admin or request.user.is_manager or
                voucher.created_by == request.user):
            return Response(
                {'detail': 'You do not have permission to view this voucher\'s usage history.'},
                status=status.HTTP_403_FORBIDDEN
            )

        usages = voucher.usages.select_related('user', 'voucher').order_by('-used_at')
        serializer = VoucherUsageSerializer(usages, many=True)

        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def use_voucher(self, request, pk=None):
        """
        Record usage of a voucher.

        POST /api/vouchers/{id}/use_voucher/
        Body: {
            "purchase_amount": "100.00",
            "discount_applied": "10.00"
        }
        """
        voucher = self.get_object()

        # Create usage record
        data = {
            'voucher_code': voucher.code,
            'purchase_amount': request.data.get('purchase_amount'),
            'discount_applied': request.data.get('discount_applied'),
        }

        serializer = VoucherUsageCreateSerializer(
            data=data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        usage = serializer.save()

        return Response(
            VoucherUsageSerializer(usage).data,
            status=status.HTTP_201_CREATED
        )


class PercentageDiscountVoucherViewSet(viewsets.ModelViewSet):
    """
    ViewSet specifically for percentage discount vouchers.
    """
    queryset = PercentageDiscountVoucher.objects.all()
    serializer_class = PercentageDiscountVoucherSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['code', 'name']
    ordering_fields = ['created_at', 'discount_percentage']
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


class FreeShippingVoucherViewSet(viewsets.ModelViewSet):
    """
    ViewSet specifically for free shipping vouchers.
    """
    queryset = FreeShippingVoucher.objects.all()
    serializer_class = FreeShippingVoucherSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['code', 'name']
    ordering_fields = ['created_at']
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
