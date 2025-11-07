================================================================================
                    ARCHITECTURE OVERVIEW
================================================================================

                              USER BROWSER
                                   |
                                   |
                    _______________V_______________
                   |                               |
                   |         FRONTEND              |
                   |       Next.js 16              |
                   |    Port 3000                  |
                   |                               |
                   |  - TypeScript + React         |
                   |  - shadcn/ui Components       |
                   |  - Tailwind CSS               |
                   |  - Zod Validation             |
                   |  - Axios API Client           |
                   |_______________________________|
                                   |
                                   | HTTP/REST API
                                   | (CORS enabled)
                                   |
        ___________________________|_____________________________
       |                                                         |
       |                                                         |
       V                                                         V
   PORT 3000                                                 PORT 8000
   /login                                             /api/v1/auth/token/
   /register                                          /api/v1/users/
   /dashboard/users                                   /api/v1/vouchers/
   /dashboard/vouchers                                /api/v1/docs/ (Swagger)
                                                      /api/v1/redoc/ (ReDoc)
                                                      /admin/ (Django Admin)

                    _______________V_______________
                   |                               |
                   |         BACKEND               |
                   |       Django 5.1.3            |
                   |    Port 8000                  |
                   |                               |
                   |  - Django REST Framework      |
                   |  - JWT Authentication         |
                   |  - Polymorphic Models         |
                   |  - 30+ API Endpoints          |
                   |  - 176 Passing Tests          |
                   |_______________________________|
                                   |
                    _______________|_____________
                   |               |             |
                   |               |             |
                   V               V             V
         PostgreSQL 16       Redis 7        Django Admin
         Port 5432         Port 6379       Browsable API
         voucher_system     (optional)
         postgres/postgres               User Model
                                        Voucher Models
                                        (Polymorphic)

================================================================================
                            ENVIRONMENT VARIABLES
================================================================================

FRONTEND (.env.local)
├── NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

BACKEND (.env)
├── Database
│   ├── POSTGRES_DB=voucher_system
│   ├── POSTGRES_USER=postgres
│   ├── POSTGRES_PASSWORD=postgres
│   └── DATABASE_URL=postgresql://postgres:postgres@db:5432/voucher_system
├── Django
│   ├── DJANGO_SECRET_KEY=<generated-secret>
│   ├── DJANGO_DEBUG=False
│   └── DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,backend
├── JWT
│   ├── JWT_ACCESS_TOKEN_LIFETIME=60
│   └── JWT_REFRESH_TOKEN_LIFETIME=1440
└── CORS
    └── CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

================================================================================
                            DATA FLOW
================================================================================

1. USER REGISTRATION FLOW
   Browser (Frontend)
       |
       ├─→ Fill registration form
       |
       └─→ Submit POST /api/v1/auth/register/
           {email, password, first_name, last_name}
               |
               ├─→ Django validates input (Zod + DRF validators)
               |
               ├─→ Hash password (Argon2)
               |
               ├─→ Create User record in PostgreSQL
               |
               └─→ Return 201 + User object
                   {id, email, first_name, last_name, role, created_at}
                   |
                   └─→ Frontend stores response, redirects to login

2. AUTHENTICATION FLOW
   Browser (Frontend)
       |
       ├─→ Fill login form (email, password)
       |
       └─→ Submit POST /api/v1/auth/token/
           {email, password}
               |
               ├─→ Django verifies credentials
               |
               ├─→ Generate JWT tokens
               |
               └─→ Return 200
                   {access: <token>, refresh: <token>}
                   |
                   ├─→ Frontend stores tokens in localStorage
                   |
                   ├─→ Sets Authorization header: Bearer <access_token>
                   |
                   └─→ Redirects to /dashboard

3. PROTECTED REQUEST FLOW
   Frontend (all subsequent requests)
       |
       └─→ Include Authorization header
           "Authorization: Bearer <access_token>"
               |
               ├─→ Axios interceptor adds header automatically
               |
               ├─→ Django JWT middleware validates token
               |
               ├─→ Authenticate user
               |
               ├─→ Check permissions
               |
               └─→ Execute API logic
                   {return response with 200/401/403/404/etc}

4. VOUCHER CREATION FLOW
   Browser Frontend (Authenticated)
       |
       ├─→ Navigate to /dashboard/vouchers/new
       |
       ├─→ Fill form (code, name, type: percentage/fixed/free_shipping, ...)
       |
       └─→ Submit POST /api/v1/vouchers/
           {code, name, status, type_specific_fields...}
               |
               ├─→ Django validates (Zod + DRF serializer)
               |
               ├─→ Check permissions (admin/manager only)
               |
               ├─→ Check N+1 queries (optimized queries)
               |
               ├─→ Create polymorphic Voucher record
               |
               ├─→ Store in PostgreSQL
               |
               └─→ Return 201 + Voucher object
                   {id, code, name, type, status, discount_value, created_at}
                   |
                   └─→ Frontend updates list, shows success notification

================================================================================
                        DOCKER SERVICES
================================================================================

docker-compose up -d --build

┌─────────────────────────────────────────────────────────────┐
│                     Docker Network                          │
│                   (voucher_network)                         │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                    PostgreSQL                         │  │
│  │  Container: voucher_db                               │  │
│  │  Image: postgres:16-alpine                           │  │
│  │  Port: 5432 → 5432                                   │  │
│  │  Volume: postgres_data:/var/lib/postgresql/data      │  │
│  │  Healthcheck: pg_isready (every 10s)                 │  │
│  └───────────────────────────────────────────────────────┘  │
│                           ▲                                  │
│                           │                                  │
│                           │ Database Connection              │
│                           │                                  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                     Django Backend                    │  │
│  │  Container: voucher_backend                          │  │
│  │  Image: Custom (FROM python:3.12-slim)              │  │
│  │  Port: 8000 → 8000                                   │  │
│  │  Depends on: db (healthy), redis (healthy)          │  │
│  │  Healthcheck: curl /api/v1/health/ (every 30s)      │  │
│  │  Volumes:                                            │  │
│  │    - ./backend/staticfiles:/app/staticfiles          │  │
│  │    - ./backend/mediafiles:/app/mediafiles            │  │
│  └───────────────────────────────────────────────────────┘  │
│    ▲                                      ▲                  │
│    │ HTTP Requests                        │ Cache            │
│    │ CORS: localhost:3000                 │                  │
│    │                                      │                  │
│    │                        ┌──────────────┘                  │
│    │                        │                                 │
│  ┌─┴────────────────────────┴──────────────────────────────┐ │
│  │                     Redis Cache                         │ │
│  │  Container: voucher_redis                             │ │
│  │  Image: redis:7-alpine                                │ │
│  │  Port: 6379 → 6379                                    │ │
│  │  Volume: redis_data:/data                             │ │
│  │  Healthcheck: redis-cli incr ping (every 10s)         │ │
│  └────────────────────────────────────────────────────────┘ │
│    ▲                                                         │
│    │                                                         │
│    │ HTTP Requests                                          │
│    │                                                         │
│  ┌─┴──────────────────────────────────────────────────────┐ │
│  │                  Next.js Frontend                      │ │
│  │  Container: voucher_frontend                          │ │
│  │  Image: Custom (FROM node:20-alpine)                 │ │
│  │  Port: 3000 → 3000                                    │ │
│  │  Depends on: backend (healthy)                        │ │
│  │  Healthcheck: curl /api/health (every 30s)           │ │
│  │  Environment:                                         │ │
│  │    - NODE_ENV=production                             │ │
│  │    - NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1│ │
│  └────────────────────────────────────────────────────────┘ │
│    ▲                                                         │
│    │                                                         │
│    │ HTTP                                                    │
│    │ (Browser connects here)                                │
│    │                                                         │
└────┼─────────────────────────────────────────────────────────┘
     │
  BROWSER (localhost:3000)

================================================================================
                     QUICK START - LOCAL DEVELOPMENT
================================================================================

TERMINAL 1 - Backend
$ cd /Users/gerwin/Developer/_personal/user-voucher-django-next/backend
$ python -m venv venv
$ source venv/bin/activate
$ pip install -r requirements/development.txt
$ python manage.py migrate
$ python manage.py createsuperuser
$ python manage.py runserver
→ Backend running on http://localhost:8000

TERMINAL 2 - Frontend
$ cd /Users/gerwin/Developer/_personal/user-voucher-django-next/frontend
$ npm install
$ npm run dev
→ Frontend running on http://localhost:3000

TERMINAL 3 - Browser
$ open http://localhost:3000
→ Login / Register / Use the application

================================================================================
