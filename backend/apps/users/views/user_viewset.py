"""
User viewsets for REST API.
"""

from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response

from apps.users.enums import UserRole, UserStatus
from apps.users.serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    UserListSerializer,
    UserAdminSerializer,
    PasswordChangeSerializer,
)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User model with proper permissions and optimizations.

    Endpoints:
    - list: Get all users (admin only)
    - retrieve: Get specific user
    - create: Register new user (public)
    - update: Update user information
    - partial_update: Partially update user
    - destroy: Delete user (admin only)
    - me: Get current user profile
    - change_password: Change current user's password
    - activate: Activate user account (admin only)
    - deactivate: Deactivate user account (admin only)
    """
    queryset = User.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'status', 'is_active']
    search_fields = ['email', 'first_name', 'last_name']
    ordering_fields = ['email', 'created_at', 'date_joined']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Optimize queryset with select_related and apply user-based filtering.
        """
        queryset = super().get_queryset()

        # Admins can see all users
        if self.request.user.is_authenticated and self.request.user.is_admin:
            return queryset

        # Regular users can only see active users (and themselves)
        if self.request.user.is_authenticated:
            return queryset.filter(
                status=UserStatus.ACTIVE,
                is_active=True
            ) | queryset.filter(id=self.request.user.id)

        # Anonymous users can't list users
        return queryset.none()

    def get_serializer_class(self):
        """
        Return appropriate serializer based on action and user role.
        """
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        elif self.action == 'list':
            # Use admin serializer for admins, minimal for others
            if self.request.user.is_authenticated and self.request.user.is_admin:
                return UserAdminSerializer
            return UserListSerializer
        elif self.action == 'change_password':
            return PasswordChangeSerializer
        elif self.request.user.is_authenticated and self.request.user.is_admin:
            return UserAdminSerializer
        return UserSerializer

    def get_permissions(self):
        """
        Set permissions based on action.
        """
        if self.action == 'create':
            # Anyone can register
            permission_classes = [AllowAny]
        elif self.action in ['destroy', 'activate', 'deactivate']:
            # Only admins can delete or change user status
            permission_classes = [IsAdminUser]
        elif self.action in ['list', 'me', 'change_password']:
            # Authenticated users can list (with filtered results)
            permission_classes = [IsAuthenticated]
        elif self.action in ['retrieve', 'update', 'partial_update']:
            # Authenticated users (but can only modify their own data)
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """
        Create user with default role.
        """
        serializer.save()

    def update(self, request, *args, **kwargs):
        """
        Update user - users can only update themselves unless admin.
        """
        instance = self.get_object()

        # Check if user is updating their own profile or is admin
        if not request.user.is_admin and instance.id != request.user.id:
            return Response(
                {'detail': 'You do not have permission to update this user.'},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        Partial update user - users can only update themselves unless admin.
        """
        instance = self.get_object()

        # Check if user is updating their own profile or is admin
        if not request.user.is_admin and instance.id != request.user.id:
            return Response(
                {'detail': 'You do not have permission to update this user.'},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().partial_update(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve user - users can only see themselves unless admin.
        """
        instance = self.get_object()

        # Check if user is viewing their own profile or is admin
        if not request.user.is_admin and instance.id != request.user.id:
            return Response(
                {'detail': 'You do not have permission to view this user.'},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().retrieve(request, *args, **kwargs)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """
        Get current user's profile.

        GET /api/users/me/
        """
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        """
        Change current user's password.

        POST /api/users/change_password/
        Body: {
            "old_password": "current_password",
            "new_password": "new_password",
            "new_password_confirm": "new_password"
        }
        """
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        # Set new password
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()

        return Response(
            {'detail': 'Password changed successfully.'},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def activate(self, request, pk=None):
        """
        Activate a user account (admin only).

        POST /api/users/{id}/activate/
        """
        user = self.get_object()
        user.status = UserStatus.ACTIVE
        user.is_active = True
        user.save(update_fields=['status', 'is_active', 'updated_at'])

        serializer = self.get_serializer(user)
        return Response(
            {
                'detail': 'User activated successfully.',
                'user': serializer.data
            },
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def deactivate(self, request, pk=None):
        """
        Deactivate a user account (admin only).

        POST /api/users/{id}/deactivate/
        """
        user = self.get_object()

        # Prevent deactivating superusers
        if user.is_superuser:
            return Response(
                {'detail': 'Cannot deactivate superuser accounts.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.status = UserStatus.INACTIVE
        user.is_active = False
        user.save(update_fields=['status', 'is_active', 'updated_at'])

        serializer = self.get_serializer(user)
        return Response(
            {
                'detail': 'User deactivated successfully.',
                'user': serializer.data
            },
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def vouchers(self, request, pk=None):
        """
        Get vouchers created by this user.

        GET /api/users/{id}/vouchers/
        """
        user = self.get_object()

        # Users can only see their own vouchers unless admin
        if not request.user.is_admin and user.id != request.user.id:
            return Response(
                {'detail': 'You do not have permission to view this user\'s vouchers.'},
                status=status.HTTP_403_FORBIDDEN
            )

        vouchers = user.created_vouchers.select_related('created_by').all()

        # Import here to avoid circular dependency
        from apps.vouchers.serializers import VoucherListSerializer
        serializer = VoucherListSerializer(vouchers, many=True)

        return Response(serializer.data)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def voucher_usages(self, request, pk=None):
        """
        Get voucher usages by this user.

        GET /api/users/{id}/voucher_usages/
        """
        user = self.get_object()

        # Users can only see their own usage history unless admin
        if not request.user.is_admin and user.id != request.user.id:
            return Response(
                {'detail': 'You do not have permission to view this user\'s voucher usage.'},
                status=status.HTTP_403_FORBIDDEN
            )

        usages = user.voucher_usages.select_related('voucher', 'user').all()

        # Import here to avoid circular dependency
        from apps.vouchers.serializers import VoucherUsageSerializer
        serializer = VoucherUsageSerializer(usages, many=True)

        return Response(serializer.data)
