# Quick Start Guide

## API is Ready!

The Django REST Framework API has been successfully implemented and tested.

## Start the Development Server

```bash
cd /Users/gerwin/Developer/_personal/user-voucher-django-next/backend
source venv/bin/activate
python manage.py runserver
```

## First Time Setup

### 1. Create a Superuser

```bash
python manage.py createsuperuser
```

Enter:
- Email: admin@example.com
- First name: Admin
- Last name: User
- Password: (choose a secure password)

### 2. Access the API

- **API Documentation (Swagger)**: http://localhost:8000/api/docs/
- **API Documentation (ReDoc)**: http://localhost:8000/api/redoc/
- **Django Admin**: http://localhost:8000/admin/
- **Browsable API**: http://localhost:8000/api/users/

## Quick Test

### 1. Get JWT Token

```bash
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "your_password"
  }'
```

### 2. View Your Profile

```bash
curl -X GET http://localhost:8000/api/users/me/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 3. Create a Voucher

```bash
curl -X POST http://localhost:8000/api/percentage-vouchers/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "WELCOME10",
    "name": "Welcome 10% Discount",
    "description": "Welcome offer for new customers",
    "status": "ACTIVE",
    "valid_from": "2024-01-01T00:00:00Z",
    "valid_until": "2024-12-31T23:59:59Z",
    "usage_limit": 100,
    "discount_percentage": "10.00",
    "min_purchase_amount": "0.00"
  }'
```

### 4. Validate Voucher

```bash
curl -X POST http://localhost:8000/api/vouchers/validate/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "WELCOME10",
    "purchase_amount": "100.00"
  }'
```

## What's Implemented

✅ User Management
- Registration, authentication, profile management
- Role-based access control (Admin, Manager, User, Guest)
- JWT authentication

✅ Voucher System
- Polymorphic vouchers (Percentage, Fixed Amount, Free Shipping)
- Voucher validation and discount calculation
- Usage tracking

✅ API Features
- Filtering, searching, and ordering
- Pagination (20 items per page)
- Comprehensive validation
- Query optimization (no N+1 queries)

✅ Documentation
- Swagger UI at /api/docs/
- ReDoc at /api/redoc/
- OpenAPI schema at /api/schema/

## Main API Endpoints

### Authentication
- POST /api/auth/token/ - Get JWT token
- POST /api/auth/token/refresh/ - Refresh token

### Users
- GET /api/users/ - List users (admin only)
- POST /api/users/ - Register user (public)
- GET /api/users/me/ - Current user profile
- POST /api/users/change_password/ - Change password

### Vouchers
- GET /api/vouchers/ - List all vouchers
- POST /api/vouchers/ - Create voucher (admin/manager)
- POST /api/vouchers/validate/ - Validate voucher code
- GET /api/percentage-vouchers/ - List percentage vouchers
- GET /api/fixed-amount-vouchers/ - List fixed amount vouchers
- GET /api/free-shipping-vouchers/ - List free shipping vouchers

### Voucher Usage
- GET /api/voucher-usages/ - List usage history

## For Full Documentation

See: [API_SETUP.md](API_SETUP.md)

## System Check

To verify everything is working:

```bash
python manage.py check
```

Expected output: `System check identified no issues (0 silenced).`
