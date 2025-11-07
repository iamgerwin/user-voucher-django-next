# Request Lifecycle Walkthrough

This document provides a comprehensive walkthrough of HTTP request lifecycles in the User Voucher Django-Next.js application. It covers authentication flows and CRUD operations with detailed sequence diagrams.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Authentication Flow (JWT Login)](#authentication-flow-jwt-login)
3. [Token Refresh Flow](#token-refresh-flow)
4. [Voucher CRUD Operations](#voucher-crud-operations)
   - [Create Voucher](#create-voucher)
   - [Read/List Vouchers](#readlist-vouchers)
   - [Update Voucher](#update-voucher)
   - [Delete Voucher](#delete-voucher)
5. [Component Structure](#component-structure)
6. [API Client Architecture](#api-client-architecture)

---

## Architecture Overview

```mermaid
graph TB
    subgraph "Frontend (Next.js 16 - Port 3000)"
        UI[UI Components<br/>React Client Components]
        Hooks[Custom Hooks<br/>use-auth, use-api]
        API[API Client Layer<br/>apiClient, authApi, vouchersApi]
    end

    subgraph "Network Layer"
        Axios[Axios HTTP Client<br/>Interceptors]
        Storage[LocalStorage<br/>access_token, refresh_token, user]
    end

    subgraph "Backend (Django REST - Port 8000)"
        Routes[URL Router<br/>config/urls.py]
        Views[ViewSets & Views<br/>auth_views.py, voucher_viewset.py]
        Auth[JWT Authentication<br/>SimpleJWT]
        Serializers[DRF Serializers<br/>Validation & Serialization]
        Models[Django Models<br/>User, Voucher, etc.]
        DB[(PostgreSQL<br/>Database)]
    end

    UI --> Hooks
    Hooks --> API
    API --> Axios
    Axios <--> Storage
    Axios <-->|HTTP/JSON| Routes
    Routes --> Views
    Views --> Auth
    Views --> Serializers
    Serializers --> Models
    Models --> DB

    style UI fill:#e1f5ff
    style API fill:#fff3e0
    style Views fill:#f3e5f5
    style DB fill:#e8f5e9
```

### Technology Stack

**Frontend:**
- Next.js 16.0.1 (App Router)
- React 19.2.0
- Axios 1.13.2
- TypeScript 5
- TailwindCSS 4

**Backend:**
- Django 5.1
- Django REST Framework
- djangorestframework-simplejwt
- PostgreSQL

**Communication:**
- RESTful API (JSON)
- JWT Bearer Token Authentication
- Base URL: `http://localhost:8000/api/v1`

---

## Authentication Flow (JWT Login)

The authentication flow demonstrates how a user logs in and receives JWT tokens for subsequent authenticated requests.

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant UI as LoginForm<br/>(login-form.tsx)
    participant Hook as useAuth Hook<br/>(use-auth.ts)
    participant AuthAPI as authApi<br/>(lib/api/auth.ts)
    participant Client as apiClient<br/>(lib/api/client.ts)
    participant LS as LocalStorage
    participant Backend as Django Backend<br/>(auth_views.py)
    participant JWT as SimpleJWT<br/>(Token Generator)
    participant DB as Database

    User->>UI: Enter credentials<br/>(username, password)
    User->>UI: Click "Login"

    UI->>UI: Form validation<br/>(zod schema)
    UI->>Hook: login({username, password})

    Hook->>AuthAPI: authApi.login(credentials)
    AuthAPI->>Client: apiClient.post('/auth/login/', data)

    Note over Client: Axios Request Interceptor<br/>No token needed for login

    Client->>Backend: POST /api/v1/auth/login/<br/>Content-Type: application/json<br/>Body: {username, password}

    Backend->>Backend: Extract credentials from request.data
    Backend->>DB: User.objects.get(email=email)

    alt User Not Found
        DB-->>Backend: DoesNotExist
        Backend-->>Client: 401 Unauthorized<br/>{detail: "Invalid credentials"}
        Client-->>AuthAPI: Error Response
        AuthAPI-->>Hook: Error thrown
        Hook-->>UI: {success: false, error: message}
        UI->>User: Show error alert
    else User Found
        DB-->>Backend: User object
        Backend->>Backend: user.check_password(password)

        alt Invalid Password
            Backend-->>Client: 401 Unauthorized<br/>{detail: "Invalid credentials"}
            Client-->>AuthAPI: Error Response
            AuthAPI-->>Hook: Error thrown
            Hook-->>UI: {success: false, error: message}
            UI->>User: Show error alert
        else Password Valid
            Backend->>Backend: Check user.is_active

            alt User Inactive
                Backend-->>Client: 401 Unauthorized<br/>{detail: "User account is inactive"}
                Client-->>AuthAPI: Error Response
                AuthAPI-->>Hook: Error thrown
                Hook-->>UI: {success: false, error: message}
                UI->>User: Show error alert
            else User Active
                Backend->>JWT: RefreshToken.for_user(user)
                JWT-->>Backend: {access_token, refresh_token}

                Backend->>Backend: Serialize user data<br/>(UserSerializer)
                Backend-->>Client: 200 OK<br/>{<br/>  tokens: {access, refresh},<br/>  user: {id, email, ...}<br/>}

                Client-->>AuthAPI: Response data

                AuthAPI->>LS: setItem('access_token', tokens.access)
                AuthAPI->>LS: setItem('refresh_token', tokens.refresh)
                AuthAPI->>LS: setItem('user', JSON.stringify(user))

                AuthAPI-->>Hook: {tokens, user}

                Hook->>Hook: setUser(response.user)
                Hook->>Hook: setIsAuthenticated(true)
                Hook->>Hook: router.push('/dashboard')

                Hook-->>UI: {success: true, data: response}
                UI->>User: Redirect to Dashboard
            end
        end
    end
```

### Key Files Involved

**Frontend:**
- `/frontend/app/(auth)/login/page.tsx` - Login page component
- `/frontend/components/auth/login-form.tsx` - Login form with validation (line 20-102)
- `/frontend/hooks/use-auth.ts` - Authentication hook (line 24-36)
- `/frontend/lib/api/auth.ts` - Auth API methods (line 11-24)
- `/frontend/lib/api/client.ts` - Axios client with interceptors (line 6-115)

**Backend:**
- `/backend/config/urls.py` - URL routing (line 48)
- `/backend/apps/users/views/auth_views.py` - Login view (line 18-83)

### Data Flow Details

#### Request Payload
```json
{
  "username": "user@example.com",
  "password": "password123"
}
```

#### Success Response (200 OK)
```json
{
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  },
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "CUSTOMER",
    "is_active": true
  }
}
```

#### Error Response (401 Unauthorized)
```json
{
  "detail": "Invalid credentials."
}
```

### LocalStorage State After Login

| Key | Value |
|-----|-------|
| `access_token` | JWT access token (expires in 15-60 min) |
| `refresh_token` | JWT refresh token (expires in 7-30 days) |
| `user` | JSON stringified user object |

---

## Token Refresh Flow

The token refresh flow is automatically triggered when an API request returns 401 Unauthorized, indicating an expired access token.

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Component as React Component
    participant API as vouchersApi
    participant Client as apiClient
    participant Interceptor as Response Interceptor<br/>(client.ts)
    participant LS as LocalStorage
    participant Backend as Django Backend
    participant JWT as SimpleJWT

    User->>Component: Trigger action<br/>(e.g., load vouchers)
    Component->>API: getVouchers()
    API->>Client: apiClient.get('/vouchers/')

    Note over Client: Request Interceptor adds<br/>Authorization: Bearer {expired_token}

    Client->>Backend: GET /api/v1/vouchers/<br/>Authorization: Bearer {expired_token}

    Backend->>Backend: Validate JWT token
    Backend->>Backend: Token expired!
    Backend-->>Client: 401 Unauthorized

    Client->>Interceptor: Error response (401)
    Interceptor->>Interceptor: Check: status === 401<br/>AND !originalRequest._retry

    Interceptor->>Interceptor: Set originalRequest._retry = true
    Interceptor->>LS: getItem('refresh_token')
    LS-->>Interceptor: refresh_token

    alt No Refresh Token
        Interceptor->>LS: Clear all tokens and user
        Interceptor->>Interceptor: window.location.href = '/login'
        Interceptor-->>Component: Redirect to login
    else Refresh Token Exists
        Interceptor->>Backend: POST /api/v1/auth/refresh/<br/>{refresh: refresh_token}

        Backend->>JWT: Validate refresh token

        alt Refresh Token Invalid/Expired
            JWT-->>Backend: TokenError
            Backend-->>Interceptor: 401 Unauthorized
            Interceptor->>LS: Clear all tokens and user
            Interceptor->>Interceptor: window.location.href = '/login'
            Interceptor-->>Component: Redirect to login
        else Refresh Token Valid
            JWT-->>Backend: Generate new access token
            Backend-->>Interceptor: 200 OK<br/>{access: new_access_token}

            Interceptor->>LS: setItem('access_token', new_access_token)
            Interceptor->>Interceptor: Update originalRequest headers<br/>Authorization: Bearer {new_access_token}

            Interceptor->>Backend: Retry original request<br/>GET /api/v1/vouchers/<br/>Authorization: Bearer {new_access_token}

            Backend->>Backend: Validate new token
            Backend-->>Client: 200 OK + Data
            Client-->>API: Response data
            API-->>Component: Vouchers data
            Component->>User: Display data
        end
    end
```

### Key Implementation

**Location:** `/frontend/lib/api/client.ts` (line 38-79)

The response interceptor automatically:
1. Detects 401 Unauthorized responses
2. Retrieves refresh token from localStorage
3. Requests new access token
4. Retries original request with new token
5. Redirects to login if refresh fails

This implementation ensures **seamless user experience** - users don't notice token expiration as long as the refresh token is valid.

---

## Voucher CRUD Operations

### Create Voucher

Creating a voucher requires authentication and specific permissions (admin or manager role).

```mermaid
sequenceDiagram
    autonumber
    actor User as Admin/Manager User
    participant Page as New Voucher Page<br/>(vouchers/new/page.tsx)
    participant Form as VoucherForm<br/>(voucher-form.tsx)
    participant API as vouchersApi<br/>(lib/api/vouchers.ts)
    participant Client as apiClient
    participant LS as LocalStorage
    participant Backend as VoucherViewSet<br/>(voucher_viewset.py)
    participant Serializer as VoucherCreateSerializer
    participant DB as Database

    User->>Page: Navigate to /vouchers/new
    Page->>Form: Render VoucherForm component

    User->>Form: Fill form fields<br/>(code, name, type, discount, etc.)
    User->>Form: Click "Create Voucher"

    Form->>Form: Client-side validation<br/>(zod schema)

    alt Validation Failed
        Form->>User: Show validation errors
    else Validation Passed
        Form->>Form: Set isLoading = true
        Form->>API: createVoucher(formData)
        API->>Client: apiClient.post('/vouchers/', data)

        Note over Client: Request Interceptor
        Client->>LS: getItem('access_token')
        LS-->>Client: access_token
        Client->>Client: Add header:<br/>Authorization: Bearer {access_token}

        Client->>Backend: POST /api/v1/vouchers/<br/>Authorization: Bearer {token}<br/>Content-Type: application/json<br/>Body: {voucher data}

        Backend->>Backend: Check authentication<br/>(IsAuthenticated)

        alt Not Authenticated
            Backend-->>Client: 401 Unauthorized
            Note over Client: Interceptor triggers<br/>token refresh flow
        else Authenticated
            Backend->>Backend: Check permissions<br/>(is_admin or is_manager)

            alt Insufficient Permissions
                Backend-->>Client: 403 Forbidden<br/>{detail: "Only admins and managers..."}
                Client-->>API: Error thrown
                API-->>Form: Error caught
                Form->>Form: Set error state
                Form->>User: Show error message
            else Has Permission
                Backend->>Serializer: VoucherCreateSerializer(data=data)
                Serializer->>Serializer: Validate voucher type
                Serializer->>Serializer: Validate required fields<br/>by voucher type

                alt Validation Failed
                    Serializer-->>Backend: ValidationError
                    Backend-->>Client: 400 Bad Request<br/>{field errors}
                    Client-->>API: Error thrown
                    API-->>Form: Error caught
                    Form->>Form: Set field errors
                    Form->>User: Show field-specific errors
                else Validation Passed
                    Backend->>Backend: perform_create(serializer)
                    Backend->>Serializer: save(created_by=request.user)

                    Serializer->>DB: INSERT voucher record
                    DB-->>Serializer: Voucher object created

                    Serializer-->>Backend: Voucher instance

                    Backend->>Backend: Get appropriate serializer<br/>based on voucher type
                    Backend->>Backend: Serialize response

                    Backend-->>Client: 201 Created<br/>{voucher data with id}

                    Client-->>API: Response data
                    API-->>Form: Voucher object

                    Form->>Form: Set isLoading = false
                    Form->>Form: router.push(`/vouchers/${id}`)
                    Form->>User: Redirect to voucher detail page
                end
            end
        end
    end
```

#### Request Example

```http
POST /api/v1/vouchers/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
Content-Type: application/json

{
  "voucher_type": "PERCENTAGE",
  "code": "SUMMER2025",
  "name": "Summer Sale",
  "description": "Get 20% off on all items",
  "discount_percentage": "20.00",
  "max_discount_amount": "100.00",
  "min_purchase_amount": "50.00",
  "valid_from": "2025-06-01T00:00:00Z",
  "valid_until": "2025-08-31T23:59:59Z",
  "max_usage_count": 1000,
  "status": "ACTIVE"
}
```

#### Response Example

```json
{
  "id": 15,
  "code": "SUMMER2025",
  "name": "Summer Sale",
  "description": "Get 20% off on all items",
  "voucher_type": "PERCENTAGE",
  "discount_percentage": "20.00",
  "max_discount_amount": "100.00",
  "min_purchase_amount": "50.00",
  "valid_from": "2025-06-01T00:00:00Z",
  "valid_until": "2025-08-31T23:59:59Z",
  "max_usage_count": 1000,
  "usage_count": 0,
  "status": "ACTIVE",
  "created_by": {
    "id": 1,
    "email": "admin@example.com",
    "first_name": "Admin",
    "last_name": "User"
  },
  "created_at": "2025-11-07T10:30:00Z",
  "updated_at": "2025-11-07T10:30:00Z"
}
```

**Key Files:**
- Frontend: `/frontend/app/(dashboard)/vouchers/new/page.tsx` (line 1-22)
- Frontend: `/frontend/components/vouchers/voucher-form.tsx` (line 1-200+)
- Frontend: `/frontend/lib/api/vouchers.ts` (line 25-27)
- Backend: `/backend/apps/vouchers/views/voucher_viewset.py` (line 169-192)

---

### Read/List Vouchers

Listing vouchers with pagination, filtering, and role-based access control.

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Page as Vouchers Page<br/>(vouchers/page.tsx)
    participant API as vouchersApi
    participant Client as apiClient
    participant Backend as VoucherViewSet<br/>(voucher_viewset.py)
    participant QS as get_queryset()<br/>(Role-based filtering)
    participant DB as Database

    User->>Page: Navigate to /vouchers
    Page->>Page: useEffect() on mount

    Page->>API: getVouchers(page=1, limit=10)
    API->>Client: apiClient.get('/vouchers/?page=1&limit=10')

    Note over Client: Request Interceptor adds<br/>Authorization header

    Client->>Backend: GET /api/v1/vouchers/?page=1&limit=10<br/>Authorization: Bearer {token}

    Backend->>Backend: Authenticate user from JWT
    Backend->>Backend: Check permissions<br/>(IsAuthenticated)

    alt Not Authenticated
        Backend-->>Client: 401 Unauthorized
        Note over Client: Token refresh flow triggered
    else Authenticated
        Backend->>QS: get_queryset()
        QS->>QS: Check user role

        alt User is Admin or Manager
            QS->>DB: SELECT * FROM vouchers<br/>ORDER BY created_at DESC
            Note over QS: Can see ALL vouchers<br/>(including inactive)
        else User is Regular Customer
            QS->>DB: SELECT * FROM vouchers<br/>WHERE status='ACTIVE'<br/>ORDER BY created_at DESC
            Note over QS: Can only see ACTIVE vouchers
        end

        DB-->>QS: Voucher queryset
        QS-->>Backend: Filtered queryset

        Backend->>Backend: Apply pagination<br/>(page 1, limit 10)
        Backend->>Backend: list() method:<br/>Serialize each voucher<br/>with type-specific serializer

        Backend->>Backend: For each voucher:<br/>- PercentageDiscountVoucher →<br/>  PercentageDiscountVoucherSerializer<br/>- FixedAmountVoucher →<br/>  FixedAmountVoucherSerializer<br/>- FreeShippingVoucher →<br/>  FreeShippingVoucherSerializer

        Backend-->>Client: 200 OK<br/>{<br/>  count: 45,<br/>  next: "/api/v1/vouchers/?page=2",<br/>  previous: null,<br/>  results: [voucher array]<br/>}

        Client-->>API: Response data
        API-->>Page: VoucherListResponse

        Page->>Page: setVouchers(response.results)
        Page->>Page: setIsLoading(false)
        Page->>User: Display VoucherList component
    end
```

#### Request Example

```http
GET /api/v1/vouchers/?page=1&limit=10&status=active&search=summer
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

#### Response Example

```json
{
  "count": 45,
  "next": "http://localhost:8000/api/v1/vouchers/?page=2&limit=10",
  "previous": null,
  "results": [
    {
      "id": 15,
      "code": "SUMMER2025",
      "name": "Summer Sale",
      "voucher_type": "PERCENTAGE",
      "discount_percentage": "20.00",
      "status": "ACTIVE",
      "usage_count": 125,
      "max_usage_count": 1000,
      "created_at": "2025-11-07T10:30:00Z"
    },
    {
      "id": 14,
      "code": "FIXED50",
      "name": "Fixed $50 Off",
      "voucher_type": "FIXED_AMOUNT",
      "discount_amount": "50.00",
      "status": "ACTIVE",
      "usage_count": 89,
      "max_usage_count": 500,
      "created_at": "2025-11-06T15:20:00Z"
    }
  ]
}
```

**Key Features:**
- **Pagination**: Default 10 items per page (configurable)
- **Role-based filtering**: Regular users see only ACTIVE vouchers
- **Search**: Filter by code, name, or description
- **Ordering**: Sort by created_at, usage_count, etc.
- **Polymorphic serialization**: Each voucher type gets correct serializer

**Key Files:**
- Frontend: `/frontend/app/(dashboard)/vouchers/page.tsx` (line 1-60+)
- Frontend: `/frontend/lib/api/vouchers.ts` (line 13-17)
- Backend: `/backend/apps/vouchers/views/voucher_viewset.py` (line 53-72, 131-167)

---

### Update Voucher

Updating a voucher with partial updates (PATCH) support.

```mermaid
sequenceDiagram
    autonumber
    actor User as Admin/Manager
    participant Page as Edit Voucher Page<br/>(vouchers/[id]/page.tsx)
    participant Form as VoucherForm<br/>(voucher-form.tsx)
    participant API as vouchersApi
    participant Client as apiClient
    participant Backend as VoucherViewSet<br/>(voucher_viewset.py)
    participant Serializer as Voucher Serializer<br/>(Type-specific)
    participant DB as Database

    User->>Page: Navigate to /vouchers/{id}
    Page->>API: getVoucherById(id)
    API->>Client: apiClient.get('/vouchers/{id}/')
    Client->>Backend: GET /api/v1/vouchers/{id}/
    Backend->>DB: SELECT voucher WHERE id={id}
    DB-->>Backend: Voucher data
    Backend-->>Client: 200 OK + voucher data
    Client-->>API: Voucher object
    API-->>Page: Voucher data
    Page->>Form: Render form with existing data

    User->>Form: Modify fields<br/>(e.g., change discount amount)
    User->>Form: Click "Update Voucher"

    Form->>Form: Validate changes
    Form->>API: updateVoucher(id, changedData)
    API->>Client: apiClient.patch('/vouchers/{id}/', data)

    Note over Client: Request Interceptor adds<br/>Authorization header

    Client->>Backend: PATCH /api/v1/vouchers/{id}/<br/>Authorization: Bearer {token}<br/>Body: {changed fields only}

    Backend->>Backend: Check authentication
    Backend->>Backend: Check permissions<br/>(is_admin or is_manager)

    alt Insufficient Permissions
        Backend-->>Client: 403 Forbidden
        Client-->>API: Error
        API-->>Form: Error
        Form->>User: Show error message
    else Has Permission
        Backend->>DB: SELECT voucher WHERE id={id}
        DB-->>Backend: Current voucher

        Backend->>Backend: Get serializer based<br/>on voucher type
        Backend->>Serializer: Serializer(instance, data=data, partial=True)

        Serializer->>Serializer: Validate changed fields

        alt Validation Failed
            Serializer-->>Backend: ValidationError
            Backend-->>Client: 400 Bad Request<br/>{field errors}
            Client-->>API: Error
            API-->>Form: Error
            Form->>User: Show field errors
        else Validation Passed
            Backend->>Backend: perform_update(serializer)
            Backend->>Serializer: save()

            Serializer->>DB: UPDATE vouchers<br/>SET {changed fields}<br/>WHERE id={id}
            DB-->>Serializer: Updated voucher

            Serializer-->>Backend: Voucher instance
            Backend->>Backend: Serialize response

            Backend-->>Client: 200 OK<br/>{updated voucher data}

            Client-->>API: Response data
            API-->>Form: Updated voucher

            Form->>Form: Show success message
            Form->>Form: router.push(`/vouchers/${id}`)
            Form->>User: Redirect to detail page
        end
    end
```

#### Request Example (PATCH - Partial Update)

```http
PATCH /api/v1/vouchers/15/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
Content-Type: application/json

{
  "discount_percentage": "25.00",
  "max_discount_amount": "150.00",
  "status": "ACTIVE"
}
```

#### Response Example

```json
{
  "id": 15,
  "code": "SUMMER2025",
  "name": "Summer Sale",
  "description": "Get 25% off on all items",
  "voucher_type": "PERCENTAGE",
  "discount_percentage": "25.00",
  "max_discount_amount": "150.00",
  "min_purchase_amount": "50.00",
  "valid_from": "2025-06-01T00:00:00Z",
  "valid_until": "2025-08-31T23:59:59Z",
  "max_usage_count": 1000,
  "usage_count": 125,
  "status": "ACTIVE",
  "created_by": {
    "id": 1,
    "email": "admin@example.com"
  },
  "created_at": "2025-11-07T10:30:00Z",
  "updated_at": "2025-11-07T14:25:00Z"
}
```

**Key Features:**
- **Partial Updates**: Only send changed fields (PATCH)
- **Full Updates**: Send all fields (PUT) - also supported
- **Permission Check**: Only admins/managers can update
- **Type-specific validation**: Different rules for each voucher type

**Key Files:**
- Frontend: `/frontend/lib/api/vouchers.ts` (line 30-35)
- Backend: `/backend/apps/vouchers/views/voucher_viewset.py` (line 194-203)

---

### Delete Voucher

Deleting a voucher (admin-only operation).

```mermaid
sequenceDiagram
    autonumber
    actor User as Admin User
    participant Page as Voucher Detail Page
    participant Dialog as Confirmation Dialog
    participant API as vouchersApi
    participant Client as apiClient
    participant Backend as VoucherViewSet<br/>(voucher_viewset.py)
    participant DB as Database

    User->>Page: View voucher detail
    User->>Page: Click "Delete Voucher" button

    Page->>Dialog: Open confirmation dialog
    Dialog->>User: "Are you sure you want<br/>to delete this voucher?"

    User->>Dialog: Click "Confirm Delete"

    Dialog->>Page: onConfirm()
    Page->>Page: Set isDeleting = true
    Page->>API: deleteVoucher(voucherId)
    API->>Client: apiClient.delete(`/vouchers/${id}/`)

    Note over Client: Request Interceptor adds<br/>Authorization header

    Client->>Backend: DELETE /api/v1/vouchers/{id}/<br/>Authorization: Bearer {token}

    Backend->>Backend: Check authentication
    Backend->>Backend: Check permissions<br/>(IsAdminUser ONLY)

    alt Not Admin
        Backend-->>Client: 403 Forbidden<br/>{detail: "Admin permission required"}
        Client-->>API: Error thrown
        API-->>Page: Error caught
        Page->>Page: Set error message
        Page->>Page: Set isDeleting = false
        Page->>User: Show error notification
    else Is Admin
        Backend->>DB: SELECT voucher WHERE id={id}

        alt Voucher Not Found
            DB-->>Backend: DoesNotExist
            Backend-->>Client: 404 Not Found
            Client-->>API: Error
            API-->>Page: Error
            Page->>User: Show "Voucher not found"
        else Voucher Found
            DB-->>Backend: Voucher object

            Note over Backend: Check if voucher has<br/>related usage records
            Backend->>DB: Check VoucherUsage<br/>WHERE voucher_id={id}

            alt Has Usage Records
                DB-->>Backend: Usage records exist
                Note over Backend: Soft delete or cascade<br/>based on model configuration
            end

            Backend->>DB: DELETE FROM vouchers<br/>WHERE id={id}
            DB-->>Backend: Deletion successful

            Backend-->>Client: 204 No Content

            Client-->>API: Success (no content)
            API-->>Page: Deletion confirmed

            Page->>Page: Set isDeleting = false
            Page->>Page: Show success notification
            Page->>Page: router.push('/vouchers')
            Page->>User: Redirect to vouchers list
        end
    end
```

#### Request Example

```http
DELETE /api/v1/vouchers/15/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

#### Response Example

```http
HTTP/1.1 204 No Content
```

**Key Features:**
- **Admin-only**: Only users with `is_admin=True` can delete
- **Confirmation required**: UI requires explicit confirmation
- **Cascade handling**: Related usage records handled per model config
- **No content response**: Returns 204 (No Content) on success

**Key Files:**
- Frontend: `/frontend/lib/api/vouchers.ts` (line 38-40)
- Backend: `/backend/apps/vouchers/views/voucher_viewset.py` (line 31, 112-113)

---

## Component Structure

### Frontend Component Hierarchy

```mermaid
graph TB
    subgraph "Authentication Flow"
        LoginPage[LoginPage<br/>page.tsx]
        LoginForm[LoginForm<br/>login-form.tsx<br/>'use client']
        useAuth[useAuth Hook<br/>use-auth.ts]
    end

    subgraph "Voucher Management"
        VouchersPage[VouchersPage<br/>page.tsx<br/>'use client']
        VoucherNewPage[VoucherNewPage<br/>new/page.tsx]
        VoucherDetailPage[VoucherDetailPage<br/>[id]/page.tsx<br/>'use client']

        VoucherList[VoucherList<br/>voucher-list.tsx<br/>'use client']
        VoucherCard[VoucherCard<br/>voucher-card.tsx<br/>'use client']
        VoucherForm[VoucherForm<br/>voucher-form.tsx<br/>'use client']
    end

    subgraph "API Layer"
        authApi[authApi<br/>lib/api/auth.ts]
        vouchersApi[vouchersApi<br/>lib/api/vouchers.ts]
        apiClient[apiClient<br/>lib/api/client.ts]
    end

    subgraph "State Management"
        LocalStorage[(LocalStorage<br/>access_token<br/>refresh_token<br/>user)]
        ReactState[React State<br/>useState, useEffect]
    end

    LoginPage --> LoginForm
    LoginForm --> useAuth
    useAuth --> authApi

    VouchersPage --> VoucherList
    VoucherList --> VoucherCard
    VoucherNewPage --> VoucherForm
    VoucherDetailPage --> VoucherCard
    VoucherDetailPage --> VoucherForm

    VoucherList --> vouchersApi
    VoucherForm --> vouchersApi
    VoucherCard --> vouchersApi

    authApi --> apiClient
    vouchersApi --> apiClient

    apiClient <--> LocalStorage
    LoginForm --> ReactState
    VouchersPage --> ReactState

    style LoginForm fill:#ffebee
    style VoucherList fill:#e3f2fd
    style VoucherForm fill:#e3f2fd
    style apiClient fill:#fff3e0
    style LocalStorage fill:#f3e5f5
```

### Backend Architecture

```mermaid
graph TB
    subgraph "URL Routing"
        MainURLs[config/urls.py<br/>Main URL Configuration]
        UsersURLs[apps/users/urls.py<br/>User Routes]
        VouchersURLs[apps/vouchers/urls.py<br/>Voucher Routes]
    end

    subgraph "Views Layer"
        AuthViews[auth_views.py<br/>login_view<br/>register_view<br/>logout_view]
        UserViewSet[UserViewSet<br/>user_viewset.py]
        VoucherViewSet[VoucherViewSet<br/>voucher_viewset.py]
    end

    subgraph "Serializers Layer"
        UserSerializers[User Serializers<br/>UserSerializer<br/>UserCreateSerializer<br/>UserUpdateSerializer]
        VoucherSerializers[Voucher Serializers<br/>VoucherSerializer<br/>VoucherCreateSerializer<br/>Type-specific Serializers]
    end

    subgraph "Models Layer"
        UserModel[User Model<br/>Custom AbstractUser]
        VoucherModel[Voucher Models<br/>Voucher (Base)<br/>PercentageDiscountVoucher<br/>FixedAmountVoucher<br/>FreeShippingVoucher]
        UsageModel[VoucherUsage Model]
    end

    subgraph "Authentication"
        JWT[SimpleJWT<br/>Token Generation<br/>Token Validation<br/>Token Refresh]
    end

    MainURLs --> AuthViews
    MainURLs --> UsersURLs
    MainURLs --> VouchersURLs
    UsersURLs --> UserViewSet
    VouchersURLs --> VoucherViewSet

    AuthViews --> JWT
    AuthViews --> UserSerializers
    UserViewSet --> UserSerializers
    VoucherViewSet --> VoucherSerializers

    UserSerializers --> UserModel
    VoucherSerializers --> VoucherModel
    VoucherSerializers --> UsageModel

    UserViewSet --> JWT
    VoucherViewSet --> JWT

    style AuthViews fill:#ffebee
    style JWT fill:#fff3e0
    style VoucherViewSet fill:#e3f2fd
    style VoucherModel fill:#e8f5e9
```

---

## API Client Architecture

### Axios Interceptor Flow

```mermaid
flowchart TB
    Start([API Request Initiated])

    Start --> ReqInt{Request Interceptor}

    ReqInt -->|Check Browser| Browser{typeof window<br/>!== 'undefined'}
    Browser -->|Yes| GetToken[Get access_token<br/>from localStorage]
    Browser -->|No| SendReq

    GetToken --> HasToken{Token exists?}
    HasToken -->|Yes| AddAuth[Add Authorization header:<br/>Bearer {token}]
    HasToken -->|No| SendReq[Send Request]

    AddAuth --> SendReq

    SendReq --> Backend[Django Backend]
    Backend --> Response{Response Status}

    Response -->|2xx Success| ResInt[Response Interceptor<br/>Pass through]
    Response -->|401 Unauthorized| CheckRetry{Check _retry flag}
    Response -->|Other Error| ResInt

    CheckRetry -->|Already retried| ClearStorage[Clear localStorage:<br/>- access_token<br/>- refresh_token<br/>- user]
    CheckRetry -->|First attempt| SetRetry[Set _retry = true]

    SetRetry --> GetRefresh[Get refresh_token<br/>from localStorage]
    GetRefresh --> HasRefresh{Refresh token<br/>exists?}

    HasRefresh -->|No| ClearStorage
    HasRefresh -->|Yes| RefreshReq[POST /auth/refresh/<br/>{refresh: token}]

    RefreshReq --> RefreshRes{Refresh Response}

    RefreshRes -->|Success| SaveNew[Save new access_token<br/>to localStorage]
    RefreshRes -->|Failed| ClearStorage

    SaveNew --> UpdateReq[Update original request<br/>with new token]
    UpdateReq --> RetryReq[Retry original request]
    RetryReq --> Backend

    ClearStorage --> Redirect[window.location.href<br/>= '/login']
    Redirect --> End1([End - User logged out])

    ResInt --> ReturnData[Return response data]
    ReturnData --> End2([End - Success])

    style ReqInt fill:#e3f2fd
    style CheckRetry fill:#fff3e0
    style RefreshReq fill:#ffebee
    style ClearStorage fill:#ffcdd2
    style SaveNew fill:#c8e6c9
```

### API Client Class Structure

**Location:** `/frontend/lib/api/client.ts`

```typescript
class ApiClient {
  private client: AxiosInstance;

  constructor() {
    // Create axios instance with base URL
    this.client = axios.create({
      baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
      headers: { 'Content-Type': 'application/json' }
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // REQUEST INTERCEPTOR
    this.client.interceptors.request.use(
      (config) => {
        // Add access token to all requests
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      }
    );

    // RESPONSE INTERCEPTOR
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401 && !error.config._retry) {
          // Token expired - attempt refresh
          error.config._retry = true;

          const refreshToken = localStorage.getItem('refresh_token');
          const response = await axios.post('/auth/refresh/', { refresh: refreshToken });

          localStorage.setItem('access_token', response.data.access);
          error.config.headers.Authorization = `Bearer ${response.data.access}`;

          return this.client(error.config); // Retry original request
        }

        return Promise.reject(error);
      }
    );
  }

  // HTTP Methods
  async get<T>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>>
  async post<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<AxiosResponse<T>>
  async patch<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<AxiosResponse<T>>
  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>>
}

export const apiClient = new ApiClient();
```

---

## Security Considerations

### Frontend Security

1. **Token Storage**: JWTs stored in `localStorage` (vulnerable to XSS)
   - Consider using `httpOnly` cookies for production
   - Implement Content Security Policy (CSP)

2. **Automatic Token Refresh**: Transparent to user
   - Access token: Short-lived (15-60 min)
   - Refresh token: Long-lived (7-30 days)

3. **Request Validation**: Client-side validation using Zod schemas
   - Validates before sending request
   - Reduces unnecessary API calls

4. **Protected Routes**: Authentication checked in components
   - `useAuth` hook provides `isAuthenticated` state
   - Redirect to login if not authenticated

### Backend Security

1. **JWT Authentication**: Using `djangorestframework-simplejwt`
   - Stateless authentication
   - Token blacklisting on logout

2. **Permission Classes**:
   - `AllowAny`: Public endpoints (login, register)
   - `IsAuthenticated`: Requires valid JWT
   - `IsAdminUser`: Requires `is_admin=True`
   - Custom role checks: Manager, Admin roles

3. **Role-Based Access Control (RBAC)**:
   - Regular users: View only active vouchers
   - Managers: Create/update vouchers
   - Admins: Full CRUD + user management

4. **Input Validation**: DRF Serializers validate all input
   - Type checking
   - Required field validation
   - Custom business logic validation

5. **CORS Configuration**: Configured to allow frontend origin
   - Restricts cross-origin requests
   - Allows credentials

---

## Performance Optimizations

### Frontend

1. **Request Caching**: Browser HTTP cache for GET requests
2. **Optimistic Updates**: Update UI before API confirmation (optional)
3. **Debounced Search**: Reduce API calls on search input
4. **Pagination**: Load data in chunks (default: 10 items)
5. **Parallel Requests**: Use `Promise.all()` for independent requests

### Backend

1. **Database Query Optimization**:
   - `select_related()`: Join foreign keys in single query
   - `prefetch_related()`: Optimize reverse relations
   - Example: `queryset.select_related('created_by', 'polymorphic_ctype')`

2. **Pagination**: DRF pagination (default: 10 items per page)
   - Reduces data transfer
   - Improves response time

3. **Filtering at Database Level**: Django ORM filters
   - Role-based filtering in `get_queryset()`
   - Search and ordering via `DjangoFilterBackend`

4. **Serializer Optimization**: Use different serializers for list vs detail
   - `VoucherListSerializer`: Minimal fields for list view
   - `VoucherSerializer`: Full data for detail view

---

## Error Handling

### Frontend Error Flow

```mermaid
flowchart TB
    Error[API Error Occurred]

    Error --> Type{Error Type}

    Type -->|Network Error| NetError[Network/Connection Error]
    Type -->|401 Unauthorized| AuthError[Authentication Error]
    Type -->|403 Forbidden| PermError[Permission Error]
    Type -->|400 Bad Request| ValError[Validation Error]
    Type -->|404 Not Found| NotFound[Resource Not Found]
    Type -->|500 Server Error| ServerError[Server Error]

    NetError --> ShowMsg1[Show: "Connection failed.<br/>Please check your internet."]

    AuthError --> Refresh{Token refresh<br/>attempted?}
    Refresh -->|Success| Retry[Retry original request]
    Refresh -->|Failed| Logout[Clear tokens +<br/>Redirect to /login]

    PermError --> ShowMsg2[Show: "You don't have<br/>permission for this action."]

    ValError --> ParseErrors[Parse field errors<br/>from response]
    ParseErrors --> ShowField[Show field-specific<br/>error messages in form]

    NotFound --> ShowMsg3[Show: "Resource not found."]

    ServerError --> ShowMsg4[Show: "Server error occurred.<br/>Please try again later."]

    ShowMsg1 --> End([End])
    Logout --> End
    Retry --> End
    ShowMsg2 --> End
    ShowField --> End
    ShowMsg3 --> End
    ShowMsg4 --> End

    style AuthError fill:#ffebee
    style Refresh fill:#fff3e0
    style ValError fill:#e3f2fd
```

### Error Response Examples

**Validation Error (400):**
```json
{
  "code": ["Voucher code already exists."],
  "discount_percentage": ["Ensure this value is less than or equal to 100."],
  "valid_until": ["End date must be after start date."]
}
```

**Permission Error (403):**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**Not Found (404):**
```json
{
  "detail": "Not found."
}
```

---

## Conclusion

This walkthrough demonstrates the complete request lifecycle for:

1. **Authentication (JWT Login)**:
   - User credentials → Backend validation → JWT generation → Token storage
   - Automatic token refresh on expiration
   - Logout with token blacklisting

2. **Voucher CRUD Operations**:
   - **Create**: Form validation → Permission check → Database insert → Response
   - **Read**: Role-based filtering → Pagination → Type-specific serialization
   - **Update**: Partial updates (PATCH) → Validation → Database update
   - **Delete**: Admin-only → Cascade handling → No content response

3. **Key Architectural Patterns**:
   - **Client-side**: Axios interceptors, custom hooks, component composition
   - **Server-side**: ViewSets, serializers, role-based permissions
   - **Communication**: RESTful JSON API with JWT authentication

### Quick Reference

| Operation | Method | Endpoint | Auth Required | Permission |
|-----------|--------|----------|---------------|------------|
| Login | POST | `/api/v1/auth/login/` | No | AllowAny |
| Refresh Token | POST | `/api/v1/auth/refresh/` | No | AllowAny |
| List Vouchers | GET | `/api/v1/vouchers/` | Yes | IsAuthenticated |
| Create Voucher | POST | `/api/v1/vouchers/` | Yes | Admin/Manager |
| Get Voucher | GET | `/api/v1/vouchers/{id}/` | Yes | IsAuthenticated |
| Update Voucher | PATCH | `/api/v1/vouchers/{id}/` | Yes | Admin/Manager |
| Delete Voucher | DELETE | `/api/v1/vouchers/{id}/` | Yes | Admin Only |

For more details, refer to the specific code files mentioned throughout this document.
