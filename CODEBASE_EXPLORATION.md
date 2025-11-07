# Codebase Exploration Summary - User Voucher Django Next.js

## Project Overview

**Project Name:** User Voucher Django Next.js  
**Location:** `/Users/gerwin/Developer/_personal/user-voucher-django-next/`  
**Status:** Production-ready (100% complete)  
**Last Modified:** November 7, 2025

This is a full-stack user and voucher management system with a Django REST Framework backend and a Next.js 16 frontend. The system features polymorphic voucher types, JWT authentication, comprehensive testing (176 tests), and complete Docker containerization.

---

## 1. Frontend Application

### Location
`/Users/gerwin/Developer/_personal/user-voucher-django-next/frontend/`

### Technology Stack
- **Framework:** Next.js 16.0.1 (App Router)
- **Language:** TypeScript (strict mode)
- **UI Library:** shadcn/ui components
- **Styling:** Tailwind CSS 4
- **State Management:** React Hook Form
- **Validation:** Zod
- **HTTP Client:** Axios
- **Date Handling:** date-fns

### Key Dependencies (package.json)
```json
{
  "next": "16.0.1",
  "react": "19.2.0",
  "react-dom": "19.2.0",
  "@hookform/resolvers": "^5.2.2",
  "axios": "^1.13.2",
  "react-hook-form": "^7.66.0",
  "zod": "^4.1.12",
  "tailwindcss": "^4"
}
```

### Available Scripts
- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run ESLint

### Environment Configuration
**File:** `/Users/gerwin/Developer/_personal/user-voucher-django-next/frontend/.env.local`

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### Project Structure
```
frontend/
├── app/                          # Next.js App Router
│   ├── (auth)/                  # Login & Register pages
│   │   ├── login/
│   │   └── register/
│   ├── (dashboard)/             # Protected dashboard (route group)
│   │   ├── users/               # User management CRUD
│   │   │   ├── [id]/           # User detail page
│   │   │   ├── new/            # Create user form
│   │   │   └── page.tsx        # Users list
│   │   └── vouchers/            # Voucher management CRUD
│   │       ├── [id]/           # Voucher detail page
│   │       ├── new/            # Create voucher form
│   │       └── page.tsx        # Vouchers list
│   ├── layout.tsx               # Root layout
│   └── page.tsx                 # Home page
├── components/
│   ├── ui/                      # shadcn/ui components (12 components)
│   ├── auth/                    # Authentication forms
│   ├── layout/                  # Navigation, layout components
│   ├── users/                   # User-specific components
│   └── vouchers/                # Voucher-specific components
├── lib/
│   ├── api/                     # API client
│   │   ├── client.ts           # Axios instance with interceptors
│   │   ├── auth.ts             # Auth API functions
│   │   ├── users.ts            # User API functions
│   │   └── vouchers.ts         # Voucher API functions
│   ├── validations/             # Zod validation schemas
│   │   ├── auth.ts             # Login/register schemas
│   │   ├── user.ts             # User schemas
│   │   └── voucher.ts          # Voucher schemas
│   ├── constants/               # Enums, routes, endpoints
│   └── utils.ts                # Utility functions
├── types/                        # TypeScript type definitions
│   ├── auth.ts
│   ├── user.ts
│   └── voucher.ts
├── hooks/                        # Custom React hooks
│   ├── use-auth.ts              # Authentication hook
│   └── use-api.ts               # API hook
├── Dockerfile                    # Production image
├── Dockerfile.dev               # Development image
└── README.md
```

### Frontend Connection to Backend
- **API Base URL:** `http://localhost:8000/api/v1`
- **Environment Variable:** `NEXT_PUBLIC_API_URL`
- **Port:** 3000 (development and production)
- **Communication:** REST API via Axios with JWT authentication

---

## 2. Backend Application

### Location
`/Users/gerwin/Developer/_personal/user-voucher-django-next/backend/`

### Technology Stack
- **Framework:** Django 5.1.3
- **API Framework:** Django REST Framework 3.15.2
- **Database:** PostgreSQL 16 (Docker) or SQLite (local)
- **Cache:** Redis 7 (optional, for production)
- **Authentication:** JWT (djangorestframework-simplejwt)
- **Documentation:** drf-spectacular (Swagger/ReDoc)
- **Polymorphism:** django-polymorphic

### Key Dependencies (requirements/base.txt)
```
Django==5.1.3
djangorestframework==3.15.2
djangorestframework-simplejwt==5.3.1
psycopg2-binary==2.9.10
django-environ==0.11.2
django-cors-headers==4.6.0
django-polymorphic==3.1.0
drf-spectacular==0.28.0
django-redis==5.4.0
redis==5.2.0
```

### Available Management Commands
- `python manage.py runserver` - Start development server (port 8000)
- `python manage.py migrate` - Run database migrations
- `python manage.py createsuperuser` - Create admin user
- `python manage.py test` or `pytest` - Run tests
- `python manage.py collectstatic` - Collect static files

### Environment Configuration
**File:** `/Users/gerwin/Developer/_personal/user-voucher-django-next/.env` (uses root level)

```env
# Django Configuration
DJANGO_SECRET_KEY=your-secret-key-here-generate-with-openssl-rand-base64-32
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,backend

# Database
DATABASE_URL=postgresql://postgres:postgres@db:5432/voucher_system
POSTGRES_DB=voucher_system
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_PORT=5432

# Redis (optional)
REDIS_URL=redis://:redis@redis:6379/0
REDIS_PASSWORD=redis
REDIS_PORT=6379

# JWT Configuration
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440

# CORS Configuration
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Django Admin/Superuser (optional auto-creation)
DJANGO_SUPERUSER_USERNAME=
DJANGO_SUPERUSER_EMAIL=
DJANGO_SUPERUSER_PASSWORD=

# Ports
BACKEND_PORT=8000
FRONTEND_PORT=3000
```

### Project Structure
```
backend/
├── apps/
│   ├── core/                    # Base models and utilities
│   │   ├── models/
│   │   │   └── timestamped.py  # Abstract base models
│   │   ├── permissions/         # Custom permission classes
│   │   └── exceptions.py        # Custom exceptions
│   ├── users/                   # User management (modular)
│   │   ├── models/
│   │   │   ├── user.py         # Custom User model
│   │   │   └── managers.py     # Custom managers
│   │   ├── enums/
│   │   │   ├── role.py         # Role enum
│   │   │   └── status.py       # Status enum
│   │   ├── serializers/        # 4 serializer files
│   │   ├── views/              # UserViewSet
│   │   ├── factories/          # Test factories
│   │   ├── tests/              # 86 unit/integration tests
│   │   └── admin.py
│   └── vouchers/                # Voucher management (modular)
│       ├── models/
│       │   ├── base.py         # Abstract base voucher
│       │   ├── percentage_discount.py
│       │   ├── fixed_amount.py
│       │   ├── free_shipping.py
│       │   └── usage.py        # Usage tracking
│       ├── enums/
│       │   ├── status.py
│       │   └── discount_type.py
│       ├── serializers/        # 5 serializer files
│       ├── views/              # 5 ViewSets
│       ├── factories/          # Test factories
│       ├── tests/              # 90 unit/integration tests
│       └── admin.py
├── config/                      # Django settings
│   ├── settings/
│   │   ├── base.py             # Base settings
│   │   ├── development.py      # Dev overrides
│   │   ├── production.py       # Production overrides
│   │   └── test.py             # Test overrides
│   └── urls.py                 # URL routing
├── requirements/
│   ├── base.txt                # Core dependencies
│   ├── development.txt         # Dev tools (pytest, faker, etc)
│   └── production.txt          # Production additions
├── Dockerfile                   # Production image
├── Dockerfile.dev              # Development image
├── entrypoint.sh               # Startup script
├── manage.py                   # Django CLI
├── pytest.ini                  # Pytest configuration
├── conftest.py                 # Pytest fixtures
└── API_SETUP.md
```

### Django Settings
**Settings Module:** `config.settings.base` (with environment-specific overrides)

**Key Configuration in base.py:**
- REST Framework with JWT authentication
- CORS middleware for frontend communication
- PostgreSQL database via dj-database-url
- API documentation via drf-spectacular
- Custom User model
- Polymorphic support for vouchers

### Backend Connection to Frontend
- **API Base URL:** `http://localhost:8000/api/v1`
- **Port:** 8000
- **CORS Allowed Origins:** Configured via `CORS_ALLOWED_ORIGINS` env var
- **Authentication:** JWT tokens (Bearer tokens in Authorization header)
- **Health Check:** `GET /api/v1/health/`

---

## 3. API Endpoints Overview

### Authentication
```
POST   /api/v1/auth/register/          - User registration
POST   /api/v1/auth/token/             - Get JWT tokens (login)
POST   /api/v1/auth/token/refresh/     - Refresh access token
POST   /api/v1/auth/token/verify/      - Verify token validity
```

### Users
```
GET    /api/v1/users/                  - List users (paginated)
POST   /api/v1/users/                  - Create user
GET    /api/v1/users/{id}/             - Get user details
PUT    /api/v1/users/{id}/             - Update user
DELETE /api/v1/users/{id}/             - Delete user
GET    /api/v1/users/me/               - Get current user profile
POST   /api/v1/users/{id}/change_password/ - Change password
```

### Vouchers
```
GET    /api/v1/vouchers/               - List all vouchers
POST   /api/v1/vouchers/               - Create voucher
GET    /api/v1/vouchers/{id}/          - Get voucher details
PUT    /api/v1/vouchers/{id}/          - Update voucher
DELETE /api/v1/vouchers/{id}/          - Delete voucher
POST   /api/v1/vouchers/validate/      - Validate voucher code

# Specific voucher types
GET    /api/v1/percentage-vouchers/    - Percentage discount vouchers
GET    /api/v1/fixed-amount-vouchers/  - Fixed amount vouchers
GET    /api/v1/free-shipping-vouchers/ - Free shipping vouchers
```

### API Documentation
```
GET    /api/v1/schema/                 - OpenAPI schema
GET    /api/v1/docs/                   - Swagger UI
GET    /api/v1/redoc/                  - ReDoc documentation
```

---

## 4. Database Configuration

### PostgreSQL (Docker)
- **Container Name:** voucher_db
- **Host:** db (internal) or localhost (external)
- **Port:** 5432
- **Database:** voucher_system
- **Username:** postgres
- **Password:** postgres (use strong password in production)
- **Volume:** postgres_data (persisted)

### Redis (Docker, Optional)
- **Container Name:** voucher_redis
- **Host:** redis (internal) or localhost (external)
- **Port:** 6379
- **Password:** redis
- **Volume:** redis_data (persisted)

### Local Development Database
- **Type:** SQLite
- **File:** `backend/db.sqlite3`
- **Auto-created** on first migration

---

## 5. Docker Configuration

### Docker Compose Files
- **Production:** `/Users/gerwin/Developer/_personal/user-voucher-django-next/docker-compose.yml`
- **Development Override:** `/Users/gerwin/Developer/_personal/user-voucher-django-next/docker-compose.dev.yml`

### Services
1. **db (PostgreSQL 16-alpine)**
   - Container: voucher_db
   - Port: 5432

2. **redis (Redis 7-alpine)**
   - Container: voucher_redis
   - Port: 6379

3. **backend (Django)**
   - Container: voucher_backend
   - Port: 8000
   - Depends on: db, redis
   - Health check: GET http://localhost:8000/api/v1/health/

4. **frontend (Next.js)**
   - Container: voucher_frontend
   - Port: 3000
   - Depends on: backend
   - Health check: GET http://localhost:3000/api/health

### Docker Quick Start

**Production Mode:**
```bash
cp .env.example .env
openssl rand -base64 32  # Generate secret key
# Update DJANGO_SECRET_KEY in .env
docker-compose up -d --build
# Access: Frontend http://localhost:3000, Backend http://localhost:8000
```

**Development Mode:**
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
# Features: Hot reload, debug ports, source code mounting
```

### Health Checks
- Backend: HTTP 200 from `/api/v1/health/` every 30s
- Frontend: HTTP 200 from `/api/health` every 30s
- Start period: 40s for backend, 30s for frontend

---

## 6. How Frontend and Backend Connect

### Development Setup

**1. Backend (Terminal 1)**
```bash
cd /Users/gerwin/Developer/_personal/user-voucher-django-next/backend
source venv/bin/activate  # or python -m venv venv && activate
pip install -r requirements/development.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
# Runs on http://localhost:8000
```

**2. Frontend (Terminal 2)**
```bash
cd /Users/gerwin/Developer/_personal/user-voucher-django-next/frontend
npm install
npm run dev
# Runs on http://localhost:3000
```

### Environment Variables Connection
- **Frontend `.env.local`:** 
  ```env
  NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
  ```
  This tells the frontend where to make API calls to.

- **Backend `.env`:**
  ```env
  CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
  ```
  This allows requests from the frontend.

### API Communication Flow
1. Frontend (Port 3000) makes HTTP request to `http://localhost:8000/api/v1/endpoint`
2. Django CORS middleware validates the origin
3. Backend processes request with JWT authentication
4. Returns JSON response to frontend
5. Frontend updates UI based on response

### Authentication Flow
1. User submits login form on `/login` page
2. Frontend sends `POST /api/v1/auth/token/` with credentials
3. Backend returns `access_token` and `refresh_token`
4. Axios interceptor stores tokens and includes `Authorization: Bearer <token>` header
5. Frontend automatically refreshes token before expiration
6. User redirected to `/dashboard` on success

---

## 7. Key Files and Configuration

### Root Configuration Files
- **`.env.example`** - Environment template (all variables)
- **`docker-compose.yml`** - Production orchestration
- **`docker-compose.dev.yml`** - Development overrides
- **`README.md`** - Main documentation
- **`PROJECT_SUMMARY.md`** - Project statistics and features
- **`DOCKER_QUICK_START.md`** - Quick Docker guide

### Backend Documentation
- **`backend/API_SETUP.md`** - Complete API documentation
- **`backend/QUICK_START.md`** - Quick start guide
- **`backend/Dockerfile`** - Production image
- **`backend/Dockerfile.dev`** - Development image
- **`backend/entrypoint.sh`** - Container startup script

### Frontend Documentation
- **`frontend/README.md`** - Frontend setup and features
- **`frontend/Dockerfile`** - Production image
- **`frontend/Dockerfile.dev`** - Development image

### Deployment Documentation
- **`docs/DOCKER.md`** - Comprehensive Docker guide
- **`docs/DEPLOYMENT.md`** - VPS deployment instructions

---

## 8. Port Mapping Summary

| Service | Port | URL | Environment |
|---------|------|-----|-------------|
| Frontend | 3000 | http://localhost:3000 | Both |
| Backend | 8000 | http://localhost:8000 | Both |
| PostgreSQL | 5432 | localhost:5432 | Docker |
| Redis | 6379 | localhost:6379 | Docker (optional) |
| Swagger UI | 8000 | http://localhost:8000/api/docs/ | Both |
| ReDoc | 8000 | http://localhost:8000/api/redoc/ | Both |
| Django Admin | 8000 | http://localhost:8000/admin | Both |

---

## 9. Testing and Quality

### Backend Testing
- **Test Framework:** pytest
- **Coverage:** 176 tests, 100% passing
- **Test Files Location:** `backend/apps/*/tests/`
- **Test Database:** Separate test database (auto-created by pytest)

**Run Tests:**
```bash
cd backend
pytest                              # Run all tests
pytest --cov=apps --cov-report=html # With coverage
pytest apps/users/tests/            # Specific app
```

### Frontend Features
- TypeScript strict mode (type safety)
- Zod validation schemas
- React Hook Form with validation
- ESLint for code quality

**Run Linter:**
```bash
cd frontend
npm run lint
```

---

## 10. Quick Reference Commands

### Local Development
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements/development.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

### Docker Development
```bash
cd /Users/gerwin/Developer/_personal/user-voucher-django-next
cp .env.example .env
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
docker-compose logs -f
```

### Docker Production
```bash
docker-compose up -d --build
docker-compose exec backend python manage.py createsuperuser
```

### Accessing Services
```bash
# Frontend
open http://localhost:3000

# Backend API
open http://localhost:8000/api/v1

# API Documentation
open http://localhost:8000/api/docs/

# Django Admin
open http://localhost:8000/admin
```

---

## 11. Project Statistics

- **Total Commits:** 34 granular, incremental commits
- **Backend Tests:** 176 tests (100% passing)
- **Test Coverage:** Comprehensive unit and integration tests
- **Lines of Code:** ~15,000+ (excluding node_modules and venv)
- **API Endpoints:** 30+
- **Documentation:** 5+ comprehensive guides
- **Container Services:** 4 (PostgreSQL, Redis, Django, Next.js)

---

## 12. Security Features

- **JWT Authentication:** Token-based with refresh capability
- **CORS Protection:** Configurable allowed origins
- **HTTPS Ready:** Docker setup supports reverse proxy with SSL
- **Password Hashing:** Argon2 hashing
- **Input Validation:** Zod schemas + DRF validators
- **N+1 Query Prevention:** select_related/prefetch_related optimization
- **Environment-based Config:** Sensitive data in .env files
- **Non-root Docker User:** Security hardened containers

---

## Summary

This is a **production-ready full-stack application** with:
- Clean, modular architecture
- Comprehensive testing (176 tests)
- Complete Docker containerization
- Excellent documentation
- Security best practices
- Type safety (Python + TypeScript)
- No code smells or magic values

**To get started:** Follow the Quick Start section above or use the `DOCKER_QUICK_START.md` guide for the fastest setup.
