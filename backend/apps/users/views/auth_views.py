"""
Custom authentication views for login and registration.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import get_user_model

from apps.users.serializers import UserCreateSerializer, UserSerializer

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Custom login endpoint that returns JWT tokens.

    POST /api/auth/login/
    Body: {
        "username": "user@example.com",  # Actually the email field
        "password": "password123"
    }

    Returns:
        {
            "tokens": {
                "access": "access_token",
                "refresh": "refresh_token"
            },
            "user": {user_data}
        }
    """
    # Frontend sends 'username' but it's actually the email
    email = request.data.get('username') or request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response(
            {'detail': 'Email and password are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response(
            {'detail': 'Invalid credentials.'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    if not user.check_password(password):
        return Response(
            {'detail': 'Invalid credentials.'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    if not user.is_active:
        return Response(
            {'detail': 'User account is inactive.'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)

    # Format response to match frontend expectations
    user_data = UserSerializer(user).data
    # Add username field for frontend compatibility
    user_data['username'] = user.email

    return Response({
        'tokens': {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        },
        'user': user_data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """
    Custom registration endpoint.

    POST /api/auth/register/
    Body: {
        "username": "user@example.com",  # Actually the email field
        "email": "user@example.com",
        "password": "password123",
        "password2": "password123",
        "first_name": "John",
        "last_name": "Doe"
    }

    Returns:
        {
            "tokens": {
                "access": "access_token",
                "refresh": "refresh_token"
            },
            "user": {user_data}
        }
    """
    # Copy request data and ensure email is set from username if not provided
    data = request.data.copy()
    if 'username' in data and 'email' not in data:
        data['email'] = data['username']

    serializer = UserCreateSerializer(data=data)

    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    user = serializer.save()

    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)

    # Format response to match frontend expectations
    user_data = UserSerializer(user).data
    # Add username field for frontend compatibility
    user_data['username'] = user.email

    return Response({
        'tokens': {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        },
        'user': user_data
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def logout_view(request):
    """
    Logout endpoint that blacklists the refresh token.

    POST /api/auth/logout/
    Body: {
        "refresh": "refresh_token"
    }

    Returns:
        {
            "detail": "Successfully logged out."
        }
    """
    try:
        refresh_token = request.data.get('refresh')

        if not refresh_token:
            return Response(
                {'detail': 'Refresh token is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Blacklist the refresh token
        token = RefreshToken(refresh_token)
        token.blacklist()

        return Response(
            {'detail': 'Successfully logged out.'},
            status=status.HTTP_200_OK
        )
    except TokenError as e:
        return Response(
            {'detail': 'Invalid or expired token.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'detail': 'Logout failed.'},
            status=status.HTTP_400_BAD_REQUEST
        )
