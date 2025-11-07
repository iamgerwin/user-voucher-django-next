# User Voucher System - Django + Next.js

A full-stack user and voucher management system built with Django REST Framework and Next.js, featuring polymorphic voucher types, JWT authentication, and a modern UI with shadcn/ui.

## 🚀 Features

### Backend (Django 5.1.3)
- **Custom User Model** with email authentication
- **Polymorphic Voucher System** (Percentage, Fixed Amount, Free Shipping)
- **JWT Authentication** with token refresh
- **REST API** with comprehensive endpoints
- **Role-Based Access Control** (Admin, Manager, User, Guest)
- **Query Optimization** (select_related/prefetch_related - no N+1 queries)
- **Comprehensive Tests** (176 tests passing with pytest)
- **API Documentation** (Swagger/ReDoc with drf-spectacular)
- **Admin Interface** with polymorphic support

### Frontend (Next.js 16.0.1)
- **TypeScript** with strict mode
- **shadcn/ui** component library
- **React Server Components** by default
- **App Router** with route groups
- **JWT Authentication** with auto-refresh
- **Form Validation** with Zod and React Hook Form
- **User Management** (CRUD operations)
- **Voucher Management** (CRUD with status tracking)
- **Responsive Design** with Tailwind CSS

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [Setup Guide](#-setup-guide)
  - [Prerequisites](#prerequisites)
  - [Local Development Setup](#local-development-setup)
  - [Docker Setup](#docker-setup)
- [API Documentation](#-api-documentation)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Git Workflow](#-git-workflow)
- [Contributing](#-contributing)

## ⚡ Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd user-voucher-django-next

# Copy environment file
cp .env.example .env

# Start all services (PostgreSQL, Redis, Django, Next.js)
docker-compose up -d --build

# Create Django superuser (optional)
docker-compose exec backend python manage.py createsuperuser

# Access the applications
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# Django Admin: http://localhost:8000/admin
# API Docs: http://localhost:8000/api/docs
```

### Local Development

```bash
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements/development.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

# Frontend setup (in a new terminal)
cd frontend
npm install
npm run dev
```

## 📁 Project Structure

```
user-voucher-django-next/
├── backend/                    # Django REST API
│   ├── apps/
│   │   ├── core/              # Base models and utilities
│   │   │   ├── models/
│   │   │   │   └── timestamped.py
│   │   │   ├── permissions/
│   │   │   └── exceptions.py
│   │   ├── users/             # User management
│   │   │   ├── models/
│   │   │   │   ├── user.py
│   │   │   │   └── managers.py
│   │   │   ├── enums/
│   │   │   │   ├── role.py
│   │   │   │   └── status.py
│   │   │   ├── serializers/
│   │   │   ├── views/
│   │   │   ├── factories/
│   │   │   ├── tests/
│   │   │   └── admin.py
│   │   └── vouchers/          # Voucher management
│   │       ├── models/
│   │       │   ├── base.py
│   │       │   ├── percentage_discount.py
│   │       │   ├── fixed_amount.py
│   │       │   ├── free_shipping.py
│   │       │   └── usage.py
│   │       ├── enums/
│   │       ├── serializers/
│   │       ├── views/
│   │       ├── factories/
│   │       ├── tests/
│   │       └── admin.py
│   ├── config/                # Django settings
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── development.py
│   │   │   ├── production.py
│   │   │   └── test.py
│   │   └── urls.py
│   ├── requirements/
│   │   ├── base.txt
│   │   ├── development.txt
│   │   └── production.txt
│   ├── Dockerfile
│   ├── Dockerfile.dev
│   └── manage.py
│
├── frontend/                   # Next.js application
│   ├── app/
│   │   ├── (auth)/            # Authentication pages
│   │   │   ├── login/
│   │   │   └── register/
│   │   ├── (dashboard)/       # Protected dashboard
│   │   │   ├── users/
│   │   │   ├── vouchers/
│   │   │   └── layout.tsx
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── components/
│   │   ├── ui/                # shadcn components
│   │   ├── auth/
│   │   ├── users/
│   │   ├── vouchers/
│   │   └── layout/
│   ├── lib/
│   │   ├── api/               # API client
│   │   │   ├── client.ts
│   │   │   ├── auth.ts
│   │   │   ├── users.ts
│   │   │   └── vouchers.ts
│   │   ├── validations/       # Zod schemas
│   │   └── constants/         # Enums and routes
│   ├── types/                 # TypeScript types
│   ├── hooks/                 # Custom React hooks
│   ├── Dockerfile
│   └── Dockerfile.dev
│
├── docs/                      # Documentation
│   └── DOCKER.md
├── docker-compose.yml         # Production orchestration
├── docker-compose.dev.yml     # Development overrides
├── .env.example               # Environment template
└── README.md
```

## 🔧 Setup Guide

### Prerequisites

- **Python 3.12+** (for local development)
- **Node.js 20+** and npm (for local development)
- **Docker & Docker Compose** (for containerized setup)
- **PostgreSQL 16** (if not using Docker)
- **Redis 7** (if not using Docker)

### Local Development Setup

#### Backend Setup

1. **Create virtual environment:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements/development.txt
   ```

3. **Configure environment:**
   ```bash
   cp ../.env.example .env
   # Edit .env with your local settings
   ```

4. **Run migrations:**
   ```bash
   export DJANGO_SETTINGS_MODULE=config.settings.development
   python manage.py migrate
   ```

5. **Create superuser:**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run development server:**
   ```bash
   python manage.py runserver
   ```

7. **Run tests:**
   ```bash
   pytest -v
   ```

#### Frontend Setup

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env.local
   # Edit .env.local if needed
   ```

3. **Run development server:**
   ```bash
   npm run dev
   ```

4. **Build for production:**
   ```bash
   npm run build
   npm start
   ```

### Docker Setup

See [DOCKER_QUICK_START.md](./DOCKER_QUICK_START.md) for quick reference or [docs/DOCKER.md](./docs/DOCKER.md) for comprehensive guide.

**Quick commands:**

```bash
# Development (with hot reload)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build

# Production
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Reset everything
docker-compose down -v
```

## 📚 API Documentation

### Access API Documentation

- **Swagger UI:** http://localhost:8000/api/docs/
- **ReDoc:** http://localhost:8000/api/redoc/
- **OpenAPI Schema:** http://localhost:8000/api/schema/

### Key Endpoints

#### Authentication
- `POST /api/v1/auth/register/` - User registration
- `POST /api/v1/auth/token/` - Login (obtain JWT tokens)
- `POST /api/v1/auth/token/refresh/` - Refresh access token
- `POST /api/v1/auth/token/verify/` - Verify token

#### Users
- `GET /api/v1/users/` - List users (paginated)
- `POST /api/v1/users/` - Create user
- `GET /api/v1/users/{id}/` - Get user details
- `PUT /api/v1/users/{id}/` - Update user
- `DELETE /api/v1/users/{id}/` - Delete user
- `GET /api/v1/users/me/` - Get current user
- `POST /api/v1/users/{id}/change_password/` - Change password

#### Vouchers
- `GET /api/v1/vouchers/` - List vouchers (paginated)
- `POST /api/v1/vouchers/` - Create voucher
- `GET /api/v1/vouchers/{id}/` - Get voucher details
- `PUT /api/v1/vouchers/{id}/` - Update voucher
- `DELETE /api/v1/vouchers/{id}/` - Delete voucher
- `POST /api/v1/vouchers/{id}/validate/` - Validate voucher code

### Authentication

All protected endpoints require JWT authentication:

```bash
# Obtain tokens
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'

# Use access token
curl -X GET http://localhost:8000/api/v1/users/me/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 🧪 Testing

### Backend Tests

The backend has **176 comprehensive tests** covering:
- Models and managers
- Serializers and validation
- API endpoints and permissions
- Polymorphic voucher behavior
- Query optimization

```bash
# Run all tests
cd backend
pytest

# Run with coverage
pytest --cov=apps --cov-report=html

# Run specific test file
pytest apps/users/tests/test_models/test_user.py

# Run with markers
pytest -m unit  # Run only unit tests
pytest -m integration  # Run only integration tests
```

### Frontend Tests

```bash
cd frontend
npm test
```

## 🚀 Deployment

### Environment Configuration

1. Generate a secure Django secret key:
   ```bash
   openssl rand -base64 32
   ```

2. Update `.env` with production values:
   ```env
   DJANGO_SECRET_KEY=<generated-key>
   DJANGO_DEBUG=False
   DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   DATABASE_URL=postgresql://user:password@db:5432/dbname
   CORS_ALLOWED_ORIGINS=https://yourdomain.com
   ```

### VPS Deployment

For detailed VPS deployment instructions, see [docs/DEPLOYMENT.md](./docs/DEPLOYMENT.md).

**Quick overview:**

1. **Set up VPS** (Ubuntu 22.04 recommended)
2. **Install Docker and Docker Compose**
3. **Clone repository** to server
4. **Configure environment** (.env file)
5. **Deploy with Docker Compose:**
   ```bash
   docker-compose up -d --build
   ```

6. **Set up reverse proxy** (Nginx)
7. **Configure SSL** (Let's Encrypt)

### Production Checklist

- [ ] Set `DJANGO_DEBUG=False`
- [ ] Generate and set strong `DJANGO_SECRET_KEY`
- [ ] Configure `DJANGO_ALLOWED_HOSTS`
- [ ] Set up PostgreSQL with strong password
- [ ] Configure Redis with password
- [ ] Set up HTTPS/SSL certificates
- [ ] Configure CORS allowed origins
- [ ] Set up backup strategy for database
- [ ] Configure monitoring and logging
- [ ] Set up firewall rules
- [ ] Review and test all security settings

## 📝 Git Workflow

This project follows conventional commits for clear history:

### Commit Types

- `feat:` - New feature
- `fix:` - Bug fix
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `docs:` - Documentation changes
- `chore:` - Maintenance tasks

### Example Commits

```bash
git commit -m "feat: add user authentication endpoint"
git commit -m "fix: resolve N+1 query in voucher list"
git commit -m "refactor: split user models into separate files"
git commit -m "test: add voucher model validation tests"
git commit -m "docs: update API documentation"
```

## 🤝 Contributing

### Code Standards

**Backend (Django):**
- Follow PEP 8 style guide
- Use type hints
- Write docstrings for all public functions
- Keep models, serializers, views modular
- Prevent N+1 queries with select_related/prefetch_related
- Use enums instead of magic strings
- Write tests for new features

**Frontend (Next.js):**
- Use TypeScript strict mode
- Follow Next.js best practices
- Use React Server Components by default
- Add 'use client' only when needed
- Validate with Zod schemas
- Use enums from constants
- Write meaningful component names

### Development Workflow

1. Create feature branch from `main`
2. Implement changes with granular commits
3. Write/update tests
4. Run linters and formatters
5. Ensure all tests pass
6. Submit pull request
7. Code review and merge

### Testing Requirements

- Backend: Maintain >80% test coverage
- Frontend: Test critical user flows
- All tests must pass before merging

## 📄 License

This project is proprietary and confidential.

## 📧 Support

For questions or issues, please contact the development team.

---

**Built with:**
- Django 5.1.3
- Django REST Framework 3.15.2
- Next.js 16.0.1
- PostgreSQL 16
- Redis 7
- shadcn/ui
- TypeScript
- Docker

**Key Principles:**
- Modular architecture
- Type safety (Python & TypeScript)
- No code smells
- Comprehensive testing
- Security first
- Query optimization
- Clear documentation
