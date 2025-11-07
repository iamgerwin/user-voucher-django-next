# User Voucher System - API Setup Complete

## Overview

The Django REST Framework API has been successfully created for the user-voucher system with the following features:

- Custom User model with authentication
- Polymorphic Voucher models (Percentage Discount, Fixed Amount, Free Shipping)
- JWT authentication
- Comprehensive serializers with validation
- ViewSets with proper permissions and query optimization
- API documentation with drf-spectacular (Swagger/ReDoc)

## Project Structure

```
backend/
├── apps/
│   ├── users/
│   │   ├── serializers.py    # User serializers (6 serializers)
│   │   ├── views.py           # UserViewSet with custom actions
│   │   └── urls.py            # User API routes
│   └── vouchers/
│       ├── serializers.py     # Voucher serializers (8 serializers)
│       ├── views.py           # 5 ViewSets for vouchers
│       └── urls.py            # Voucher API routes
├── config/
│   ├── settings/
│   │   ├── base.py            # Base settings with DRF config
│   │   ├── development.py     # Development settings
│   │   ├── production.py      # Production settings
│   │   └── test.py            # Test settings
│   └── urls.py                # Main URL configuration
└── manage.py                  # Django management (uses development settings)
```

## API Endpoints

### Authentication
- `POST /api/auth/token/` - Obtain JWT token pair
- `POST /api/auth/token/refresh/` - Refresh access token
- `POST /api/auth/token/verify/` - Verify token validity

### Users
- `GET /api/users/` - List users (admin only)
- `POST /api/users/` - Register new user (public)
- `GET /api/users/{id}/` - Get user details
- `PUT /api/users/{id}/` - Update user (own profile or admin)
- `PATCH /api/users/{id}/` - Partial update user
- `DELETE /api/users/{id}/` - Delete user (admin only)
- `GET /api/users/me/` - Get current user profile
- `POST /api/users/change_password/` - Change password
- `POST /api/users/{id}/activate/` - Activate user (admin only)
- `POST /api/users/{id}/deactivate/` - Deactivate user (admin only)
- `GET /api/users/{id}/vouchers/` - Get vouchers created by user
- `GET /api/users/{id}/voucher_usages/` - Get voucher usage history

### Vouchers
- `GET /api/vouchers/` - List all vouchers
- `POST /api/vouchers/` - Create voucher (admin/manager only)
- `GET /api/vouchers/{id}/` - Get voucher details
- `PUT /api/vouchers/{id}/` - Update voucher (admin/manager only)
- `PATCH /api/vouchers/{id}/` - Partial update voucher
- `DELETE /api/vouchers/{id}/` - Delete voucher (admin only)
- `POST /api/vouchers/validate/` - Validate voucher code and calculate discount
- `GET /api/vouchers/{id}/usages/` - Get usage history for voucher
- `POST /api/vouchers/{id}/use_voucher/` - Record voucher usage

### Voucher Types (Specific Endpoints)
- `/api/percentage-vouchers/` - Percentage discount vouchers
- `/api/fixed-amount-vouchers/` - Fixed amount vouchers
- `/api/free-shipping-vouchers/` - Free shipping vouchers

### Voucher Usage
- `GET /api/voucher-usages/` - List voucher usages (filtered by user)
- `GET /api/voucher-usages/{id}/` - Get specific usage record

### Documentation
- `GET /api/schema/` - OpenAPI schema (JSON)
- `GET /api/docs/` - Swagger UI documentation
- `GET /api/redoc/` - ReDoc documentation

## Key Features Implemented

### 1. Serializers

#### User Serializers
- `UserSerializer` - Standard user serialization
- `UserCreateSerializer` - User registration with password validation
- `UserUpdateSerializer` - Update user profile
- `UserListSerializer` - Minimal serializer for list views
- `UserAdminSerializer` - Admin view with additional fields
- `PasswordChangeSerializer` - Password change validation

#### Voucher Serializers
- `VoucherSerializer` - Base voucher serialization
- `PercentageDiscountVoucherSerializer` - Percentage vouchers
- `FixedAmountVoucherSerializer` - Fixed amount vouchers
- `FreeShippingVoucherSerializer` - Free shipping vouchers
- `VoucherListSerializer` - Minimal serializer for list views
- `VoucherUsageSerializer` - Usage record serialization
- `VoucherUsageCreateSerializer` - Create usage records
- `VoucherValidateSerializer` - Validate and calculate discounts

### 2. ViewSets

#### User ViewSet
- Role-based permissions (admin, manager, user, guest)
- Custom actions: me, change_password, activate, deactivate, vouchers, voucher_usages
- Query optimization with select_related
- Filtering, searching, and ordering

#### Voucher ViewSets
- `VoucherViewSet` - Main voucher management
- `PercentageDiscountVoucherViewSet` - Specific to percentage vouchers
- `FixedAmountVoucherViewSet` - Specific to fixed amount vouchers
- `FreeShippingVoucherViewSet` - Specific to free shipping vouchers
- `VoucherUsageViewSet` - Read-only usage records
- All with query optimization (select_related, prefetch_related)
- Polymorphic serializer selection based on voucher type

### 3. Permissions & Access Control

- Public: User registration
- Authenticated: View vouchers, own profile, change password
- Manager: Create/update vouchers
- Admin: Full access to all resources

### 4. Query Optimization

All querysets use:
- `select_related()` for ForeignKey relationships
- `prefetch_related()` for reverse relationships
- Proper indexing in models

### 5. Validation

- Email validation and uniqueness
- Password strength validation
- Voucher code uniqueness
- Date range validation
- Business logic validation (min purchase amounts, discount limits)

## Setup Instructions

### 1. Verify Installation

```bash
cd /Users/gerwin/Developer/_personal/user-voucher-django-next/backend
source venv/bin/activate
python manage.py check
```

### 2. Create Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin user.

### 3. Run Development Server

```bash
python manage.py runserver
```

### 4. Access API Documentation

Open your browser and navigate to:
- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/
- Django Admin: http://localhost:8000/admin/

## Testing the API

### 1. Register a User

```bash
curl -X POST http://localhost:8000/api/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

### 2. Obtain JWT Token

```bash
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 3. Access Protected Endpoint

```bash
curl -X GET http://localhost:8000/api/users/me/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. Create a Voucher (Admin/Manager only)

```bash
curl -X POST http://localhost:8000/api/percentage-vouchers/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "SAVE20",
    "name": "20% Off Sale",
    "description": "Get 20% off your purchase",
    "status": "ACTIVE",
    "valid_from": "2024-01-01T00:00:00Z",
    "valid_until": "2024-12-31T23:59:59Z",
    "usage_limit": 100,
    "discount_percentage": "20.00",
    "min_purchase_amount": "50.00",
    "max_discount_amount": "100.00"
  }'
```

### 5. Validate a Voucher

```bash
curl -X POST http://localhost:8000/api/vouchers/validate/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "SAVE20",
    "purchase_amount": "100.00"
  }'
```

## Configuration

### Settings Files

The project uses split settings:
- `base.py` - Common settings for all environments
- `development.py` - Development-specific settings (DEBUG=True)
- `production.py` - Production settings with security
- `test.py` - Test environment settings

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Django
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Database (optional, defaults to SQLite)
DATABASE_URL=sqlite:///db.sqlite3

# JWT
JWT_ACCESS_TOKEN_LIFETIME=60  # minutes
JWT_REFRESH_TOKEN_LIFETIME=1  # days

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

## Next Steps

1. **Add More Tests**: Create unit and integration tests for all endpoints
2. **Add Permissions**: Implement custom permission classes if needed
3. **Add Throttling**: Configure API rate limiting
4. **Add Caching**: Implement caching for frequently accessed data
5. **Add Monitoring**: Set up logging and monitoring
6. **Frontend Integration**: Connect with Next.js frontend

## API Design Decisions

### Polymorphic Vouchers
- Used django-polymorphic for flexible voucher types
- Each voucher type has its own discount calculation logic
- Specific endpoints for each type + generic endpoint for all

### N+1 Query Prevention
- All querysets use select_related/prefetch_related
- Minimizes database queries for optimal performance

### Serializer Patterns
- Separate serializers for create, update, list, detail views
- Prevents exposing sensitive data (passwords)
- Optimizes data transfer for different use cases

### Permission Strategy
- ViewSet-level permission_classes for flexibility
- Method-level checks in viewset actions
- Role-based access control via User.role field

## Database Schema

The migrations have been applied with the following tables:
- `users` - Custom user model
- `vouchers` - Base voucher table (polymorphic)
- `vouchers_percentagediscountvoucher` - Percentage discount vouchers
- `vouchers_fixedamountvoucher` - Fixed amount vouchers
- `vouchers_freeshippingvoucher` - Free shipping vouchers
- `voucher_usages` - Voucher usage tracking

## Status

✅ All serializers created and validated
✅ All viewsets implemented with permissions
✅ URL routing configured
✅ Settings updated with DRF configuration
✅ Database migrations applied
✅ Import tests passing
✅ Django system checks passing
✅ Ready for development and testing

## Support

For issues or questions, refer to:
- Django REST Framework: https://www.django-rest-framework.org/
- django-polymorphic: https://django-polymorphic.readthedocs.io/
- drf-spectacular: https://drf-spectacular.readthedocs.io/
