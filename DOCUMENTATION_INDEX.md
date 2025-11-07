# Documentation Index - User Voucher Django Next.js

Complete guide to all project documentation.

---

## Start Here

**If you're new to this project, start with:**

1. **[README.md](./README.md)** - Main project overview
   - Features overview
   - Quick start instructions
   - Setup guide
   - API documentation overview
   - Contributing guidelines

2. **[CODEBASE_EXPLORATION.md](./CODEBASE_EXPLORATION.md)** - Complete technical reference
   - Frontend application structure
   - Backend application structure
   - API endpoints
   - Database configuration
   - Docker setup
   - How frontend and backend connect
   - Port mappings
   - Testing information

3. **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Visual architecture diagrams
   - System architecture overview
   - Environment variables structure
   - Data flow diagrams
   - Docker services relationships
   - Quick local development setup

4. **[DEVELOPER_QUICK_REFERENCE.md](./DEVELOPER_QUICK_REFERENCE.md)** - Task-based guide
   - Getting started (3 options)
   - Common frontend tasks
   - Common backend tasks
   - Troubleshooting
   - Command reference

---

## Documentation by Role

### For Project Managers / Stakeholders
1. **[PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md)** - Project statistics and features
2. **[README.md](./README.md)** - Feature overview
3. **[ARCHITECTURE.md](./ARCHITECTURE.md)** - System architecture

### For Frontend Developers
1. **[frontend/README.md](./frontend/README.md)** - Frontend setup and guides
2. **[CODEBASE_EXPLORATION.md](./CODEBASE_EXPLORATION.md)** - Frontend section
3. **[DEVELOPER_QUICK_REFERENCE.md](./DEVELOPER_QUICK_REFERENCE.md)** - Frontend tasks section
4. **[ARCHITECTURE.md](./ARCHITECTURE.md)** - System overview

### For Backend Developers
1. **[backend/API_SETUP.md](./backend/API_SETUP.md)** - Complete API documentation
2. **[backend/QUICK_START.md](./backend/QUICK_START.md)** - Backend quick start
3. **[CODEBASE_EXPLORATION.md](./CODEBASE_EXPLORATION.md)** - Backend section
4. **[DEVELOPER_QUICK_REFERENCE.md](./DEVELOPER_QUICK_REFERENCE.md)** - Backend tasks section
5. **[ARCHITECTURE.md](./ARCHITECTURE.md)** - System overview

### For DevOps / Deployment Engineers
1. **[DOCKER_QUICK_START.md](./DOCKER_QUICK_START.md)** - Quick Docker setup
2. **[docs/DOCKER.md](./docs/DOCKER.md)** - Comprehensive Docker guide
3. **[docs/DEPLOYMENT.md](./docs/DEPLOYMENT.md)** - VPS deployment guide
4. **[ARCHITECTURE.md](./ARCHITECTURE.md)** - System architecture
5. **[docker-compose.yml](./docker-compose.yml)** - Production configuration
6. **[docker-compose.dev.yml](./docker-compose.dev.yml)** - Development configuration

---

## Documentation Map

### Project Root
```
.
├── README.md                      # Main project documentation
├── ARCHITECTURE.md                # System architecture diagrams
├── CODEBASE_EXPLORATION.md        # Complete technical reference
├── DEVELOPER_QUICK_REFERENCE.md   # Task-based developer guide
├── DOCUMENTATION_INDEX.md         # This file
├── PROJECT_SUMMARY.md             # Project statistics
├── DOCKER_QUICK_START.md          # Quick Docker guide
├── docker-compose.yml             # Production orchestration
├── docker-compose.dev.yml         # Development overrides
├── .env.example                   # Environment variables template
│
├── docs/
│   ├── DOCKER.md                  # Comprehensive Docker guide
│   └── DEPLOYMENT.md              # VPS deployment instructions
│
├── backend/
│   ├── API_SETUP.md               # Complete API documentation
│   ├── QUICK_START.md             # Backend quick start guide
│   ├── requirements/              # Dependency management
│   │   ├── base.txt
│   │   ├── development.txt
│   │   └── production.txt
│   ├── Dockerfile                 # Production image
│   ├── Dockerfile.dev             # Development image
│   ├── entrypoint.sh              # Container startup script
│   └── apps/                      # Django apps structure
│
└── frontend/
    ├── README.md                  # Frontend documentation
    ├── package.json               # Frontend dependencies
    ├── Dockerfile                 # Production image
    ├── Dockerfile.dev             # Development image
    ├── .env.local                 # Frontend environment
    └── app/                       # Next.js application
```

---

## Quick Navigation

### Setup & Getting Started
- [Local Development Setup](./DEVELOPER_QUICK_REFERENCE.md#getting-started)
- [Docker Development Setup](./DEVELOPER_QUICK_REFERENCE.md#getting-started)
- [Docker Production Setup](./DEVELOPER_QUICK_REFERENCE.md#getting-started)
- [Quick Docker Start](./DOCKER_QUICK_START.md)

### Understanding the Project
- [Project Architecture](./ARCHITECTURE.md)
- [System Overview](./CODEBASE_EXPLORATION.md#project-overview)
- [Frontend Details](./CODEBASE_EXPLORATION.md#1-frontend-application)
- [Backend Details](./CODEBASE_EXPLORATION.md#2-backend-application)
- [Database Configuration](./CODEBASE_EXPLORATION.md#4-database-configuration)

### Development Tasks
- [Add Frontend Page](./DEVELOPER_QUICK_REFERENCE.md#add-a-new-pageroute)
- [Add Frontend Form](./DEVELOPER_QUICK_REFERENCE.md#add-form-validation)
- [Add API Integration](./DEVELOPER_QUICK_REFERENCE.md#add-api-integration)
- [Add Backend Endpoint](./DEVELOPER_QUICK_REFERENCE.md#add-new-api-endpoint)
- [Add Backend Tests](./DEVELOPER_QUICK_REFERENCE.md#add-model-tests)
- [Add Enums](./DEVELOPER_QUICK_REFERENCE.md#using-enums-for-constants)

### API Reference
- [API Endpoints](./CODEBASE_EXPLORATION.md#3-api-endpoints-overview)
- [Authentication](./backend/API_SETUP.md)
- [Users](./backend/API_SETUP.md)
- [Vouchers](./backend/API_SETUP.md)
- [Complete API Docs](./backend/API_SETUP.md)

### Troubleshooting
- [Common Issues](./DEVELOPER_QUICK_REFERENCE.md#troubleshooting)
- [CORS Errors](./DEVELOPER_QUICK_REFERENCE.md#issue-cors-error-when-calling-api-from-frontend)
- [JWT Token Issues](./DEVELOPER_QUICK_REFERENCE.md#issue-jwt-token-expired-error)
- [Port Conflicts](./DEVELOPER_QUICK_REFERENCE.md#issue-port-30008000-already-in-use)
- [Database Issues](./DEVELOPER_QUICK_REFERENCE.md#issue-database-connection-error-in-docker)
- [Test Failures](./DEVELOPER_QUICK_REFERENCE.md#issue-tests-failing-with-modulenotfounderror)

### Configuration
- [Environment Variables](./CODEBASE_EXPLORATION.md#environment-configuration)
- [Docker Configuration](./CODEBASE_EXPLORATION.md#5-docker-configuration)
- [Port Mapping](./CODEBASE_EXPLORATION.md#8-port-mapping-summary)
- [Frontend Connection](./CODEBASE_EXPLORATION.md#how-frontend-and-backend-connect)

### Deployment
- [Deployment Guide](./docs/DEPLOYMENT.md)
- [Docker Guide](./docs/DOCKER.md)
- [Production Setup](./DEVELOPER_QUICK_REFERENCE.md#option-3-docker-production)
- [Production Checklist](./README.md#production-checklist)

### Testing
- [Testing Guide](./DEVELOPER_QUICK_REFERENCE.md#testing-workflow)
- [Run Tests](./DEVELOPER_QUICK_REFERENCE.md#run-tests)
- [Backend Tests](./CODEBASE_EXPLORATION.md#9-testing-and-quality)

### Performance
- [Performance Tips](./DEVELOPER_QUICK_REFERENCE.md#performance-tips)
- [Query Optimization](./CODEBASE_EXPLORATION.md#security-features)

### Commands
- [Quick Command Reference](./DEVELOPER_QUICK_REFERENCE.md#quick-command-reference)

---

## Technology Stack Overview

### Frontend
- **Framework:** Next.js 16.0.1
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **UI Components:** shadcn/ui
- **Validation:** Zod
- **Form Handling:** React Hook Form
- **HTTP Client:** Axios
- **Documentation:** [frontend/README.md](./frontend/README.md)

### Backend
- **Framework:** Django 5.1.3
- **API:** Django REST Framework 3.15.2
- **Database:** PostgreSQL 16 (Docker) / SQLite (local)
- **Authentication:** JWT (djangorestframework-simplejwt)
- **Cache:** Redis 7
- **Documentation:** drf-spectacular (Swagger/ReDoc)
- **Testing:** pytest (176 tests)
- **Documentation:** [backend/API_SETUP.md](./backend/API_SETUP.md)

### DevOps
- **Containerization:** Docker & Docker Compose
- **Services:** PostgreSQL, Redis, Django, Next.js
- **Deployment:** Docker containers with health checks
- **Documentation:** [docs/DOCKER.md](./docs/DOCKER.md)

---

## Key Files by Purpose

### Configuration Files
- `.env.example` - Environment template
- `docker-compose.yml` - Production orchestration
- `docker-compose.dev.yml` - Development overrides
- `backend/entrypoint.sh` - Container startup script

### Backend
- `backend/manage.py` - Django management CLI
- `backend/config/settings/` - Django settings
- `backend/apps/*/models/` - Database models
- `backend/apps/*/serializers/` - API serializers
- `backend/apps/*/views/` - API views
- `backend/apps/*/tests/` - Tests

### Frontend
- `frontend/package.json` - Dependencies
- `frontend/app/` - Next.js pages and routes
- `frontend/components/` - React components
- `frontend/lib/api/` - API client
- `frontend/lib/validations/` - Validation schemas

### Documentation
- `README.md` - Main project documentation
- `ARCHITECTURE.md` - System architecture
- `CODEBASE_EXPLORATION.md` - Technical reference
- `DEVELOPER_QUICK_REFERENCE.md` - Developer guide
- `PROJECT_SUMMARY.md` - Project statistics

---

## Common Workflows

### I want to start development
1. Read [DEVELOPER_QUICK_REFERENCE.md](./DEVELOPER_QUICK_REFERENCE.md) - Getting Started
2. Choose setup option (Local, Docker Dev, or Docker Prod)
3. Follow the terminal commands
4. Open http://localhost:3000

### I need to understand the system
1. Read [ARCHITECTURE.md](./ARCHITECTURE.md) for diagrams
2. Read [CODEBASE_EXPLORATION.md](./CODEBASE_EXPLORATION.md) for details
3. Review relevant source files

### I'm adding a new feature
1. Read [DEVELOPER_QUICK_REFERENCE.md](./DEVELOPER_QUICK_REFERENCE.md) for your task
2. Follow the code examples
3. Review existing code for patterns
4. Write tests
5. Update documentation

### I'm deploying to production
1. Read [docs/DEPLOYMENT.md](./docs/DEPLOYMENT.md)
2. Review [docs/DOCKER.md](./docs/DOCKER.md)
3. Configure `.env` with production values
4. Run `docker-compose up -d --build`
5. Verify health checks and logs

### I'm troubleshooting an issue
1. Check [DEVELOPER_QUICK_REFERENCE.md - Troubleshooting](./DEVELOPER_QUICK_REFERENCE.md#troubleshooting)
2. Review relevant API docs
3. Check Docker logs: `docker-compose logs -f`
4. Review error messages in browser console / terminal

---

## Documentation Statistics

| Document | Size | Sections | Purpose |
|----------|------|----------|---------|
| README.md | 13K | 14 | Main project documentation |
| CODEBASE_EXPLORATION.md | 19K | 12 | Complete technical reference |
| ARCHITECTURE.md | 14K | 6 | Visual architecture diagrams |
| DEVELOPER_QUICK_REFERENCE.md | 16K | 13 | Task-based developer guide |
| PROJECT_SUMMARY.md | 12K | 8 | Project statistics |
| DOCKER_QUICK_START.md | 2.3K | 4 | Quick Docker setup |

**Total Documentation: 76K+ of comprehensive guides**

---

## How Documentation is Organized

### By Audience
- **Project Managers:** PROJECT_SUMMARY.md, README.md
- **Frontend Developers:** frontend/README.md, DEVELOPER_QUICK_REFERENCE.md
- **Backend Developers:** backend/API_SETUP.md, DEVELOPER_QUICK_REFERENCE.md
- **DevOps Engineers:** docs/DEPLOYMENT.md, docs/DOCKER.md

### By Purpose
- **Setup:** DOCKER_QUICK_START.md, DEVELOPER_QUICK_REFERENCE.md
- **Understanding:** ARCHITECTURE.md, CODEBASE_EXPLORATION.md
- **Development:** DEVELOPER_QUICK_REFERENCE.md
- **API Reference:** backend/API_SETUP.md
- **Deployment:** docs/DEPLOYMENT.md

### By Detail Level
- **Quick Start:** DOCKER_QUICK_START.md (2.3K)
- **Overview:** ARCHITECTURE.md (14K)
- **Detailed:** CODEBASE_EXPLORATION.md (19K)
- **Reference:** DEVELOPER_QUICK_REFERENCE.md (16K)

---

## Next Steps

### For New Team Members
1. Read README.md (5 min)
2. Read ARCHITECTURE.md (10 min)
3. Read relevant section of CODEBASE_EXPLORATION.md (15 min)
4. Set up development environment (30 min)
5. Review DEVELOPER_QUICK_REFERENCE.md (10 min)

### For New Features
1. Check DEVELOPER_QUICK_REFERENCE.md for similar tasks
2. Review existing code patterns
3. Write tests first
4. Implement feature
5. Update documentation

### For Bug Fixes
1. Find the issue in the code
2. Understand the bug
3. Add test to reproduce
4. Fix the bug
5. Verify tests pass

### For Deployment
1. Read docs/DEPLOYMENT.md
2. Configure environment
3. Test in Docker locally
4. Deploy to production
5. Monitor health checks

---

## Questions?

- **Setup Issues:** See DEVELOPER_QUICK_REFERENCE.md - Troubleshooting
- **API Questions:** See backend/API_SETUP.md
- **Architecture Questions:** See ARCHITECTURE.md
- **Development Questions:** See DEVELOPER_QUICK_REFERENCE.md
- **Deployment Questions:** See docs/DEPLOYMENT.md

---

**Documentation Version:** 1.0  
**Last Updated:** November 7, 2025  
**Project:** User Voucher Django Next.js  
**Status:** Complete and Production-Ready
