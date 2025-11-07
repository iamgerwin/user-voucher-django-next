# Developer Quick Reference - User Voucher System

Quick lookup guide for common development tasks and troubleshooting.

---

## Getting Started (Pick One)

### Option 1: Local Development (Recommended for Development)

```bash
# Clone/enter project
cd /Users/gerwin/Developer/_personal/user-voucher-django-next

# Terminal 1 - Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements/development.txt
python manage.py migrate
python manage.py createsuperuser  # Create admin user
python manage.py runserver        # Runs on http://localhost:8000

# Terminal 2 - Frontend
cd frontend
npm install
npm run dev                        # Runs on http://localhost:3000

# Terminal 3 - Browser
open http://localhost:3000
# Login with your superuser credentials
```

### Option 2: Docker Development (Recommended for Deployment Testing)

```bash
cd /Users/gerwin/Developer/_personal/user-voucher-django-next
cp .env.example .env

# Generate a secure secret key
openssl rand -base64 32
# Copy the output and paste into .env: DJANGO_SECRET_KEY=<output>

# Development with hot reload
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Create superuser in Docker
docker-compose exec backend python manage.py createsuperuser

# Open browser
open http://localhost:3000
```

### Option 3: Docker Production

```bash
cd /Users/gerwin/Developer/_personal/user-voucher-django-next
cp .env.example .env
# Update .env with secure values
docker-compose up -d --build
open http://localhost:3000
```

---

## Common Frontend Tasks

### Add a New Page/Route

**1. Create the page file:**
```bash
# For public pages (under app/):
touch frontend/app/about/page.tsx

# For protected dashboard pages:
touch frontend/app/\(dashboard\)/reports/page.tsx
```

**2. Add route constant** (`frontend/lib/constants/routes.ts`):
```typescript
export const ROUTES = {
  // ... existing routes
  REPORTS: '/dashboard/reports',
} as const;
```

**3. Create the component:**
```typescript
// frontend/app/(dashboard)/reports/page.tsx
'use client';

import { useAuth } from '@/hooks/use-auth';

export default function ReportsPage() {
  const { user } = useAuth();
  
  return (
    <div>
      <h1>Reports</h1>
      {/* Your content */}
    </div>
  );
}
```

### Add Form Validation

**1. Create Zod schema** (`frontend/lib/validations/report.ts`):
```typescript
import { z } from 'zod';

export const reportFilterSchema = z.object({
  startDate: z.date().min(new Date('2024-01-01')),
  endDate: z.date(),
}).refine(
  (data) => data.startDate <= data.endDate,
  { message: 'Start date must be before end date' }
);

export type ReportFilter = z.infer<typeof reportFilterSchema>;
```

**2. Use in component:**
```typescript
'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { reportFilterSchema } from '@/lib/validations/report';

export function ReportForm() {
  const form = useForm({
    resolver: zodResolver(reportFilterSchema),
    defaultValues: {
      startDate: new Date('2024-01-01'),
      endDate: new Date(),
    },
  });

  return (
    <form onSubmit={form.handleSubmit(onSubmit)}>
      {/* Form fields */}
    </form>
  );
}
```

### Add API Integration

**1. Create API function** (`frontend/lib/api/reports.ts`):
```typescript
import { apiClient } from './client';

export const reportsAPI = {
  getReports: async (filters?: Record<string, any>) => {
    return apiClient.get('/reports/', { params: filters });
  },
  
  getReport: async (id: string) => {
    return apiClient.get(`/reports/${id}/`);
  },
  
  exportReport: async (id: string) => {
    return apiClient.get(`/reports/${id}/export/`, {
      responseType: 'blob',
    });
  },
};
```

**2. Use in component:**
```typescript
'use client';

import { useState, useEffect } from 'react';
import { reportsAPI } from '@/lib/api/reports';

export function ReportsList() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchReports = async () => {
      try {
        const response = await reportsAPI.getReports();
        setReports(response.data);
      } catch (err) {
        setError('Failed to load reports');
      } finally {
        setLoading(false);
      }
    };

    fetchReports();
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  
  return (
    <div>
      {reports.map(report => (
        <div key={report.id}>{report.name}</div>
      ))}
    </div>
  );
}
```

### Use Enums Instead of Magic Strings

```typescript
// frontend/lib/constants/enums.ts
export enum VoucherStatus {
  ACTIVE = 'ACTIVE',
  INACTIVE = 'INACTIVE',
  EXPIRED = 'EXPIRED',
}

export enum UserRole {
  ADMIN = 'ADMIN',
  MANAGER = 'MANAGER',
  USER = 'USER',
  GUEST = 'GUEST',
}

// Use in components
import { VoucherStatus } from '@/lib/constants/enums';

if (voucher.status === VoucherStatus.ACTIVE) {
  // ...
}
```

### Debug API Calls

The Axios client logs all requests/responses in development. Check the browser console:

```typescript
// frontend/lib/api/client.ts
apiClient.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.config.url, response.data);
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data);
    return Promise.reject(error);
  }
);
```

---

## Common Backend Tasks

### Add New API Endpoint

**1. Create model** (`backend/apps/reports/models/report.py`):
```python
from apps.core.models import TimestampedModel

class Report(TimestampedModel):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    data = models.JSONField(default=dict)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
```

**2. Create serializer** (`backend/apps/reports/serializers.py`):
```python
from rest_framework import serializers
from .models import Report

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['id', 'title', 'description', 'user', 'data', 'created_at']
        read_only_fields = ['user', 'created_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
```

**3. Create viewset** (`backend/apps/reports/views.py`):
```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Report
from .serializers import ReportSerializer

class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['user', 'created_at']
    ordering_fields = ['created_at', 'title']
    
    def get_queryset(self):
        # Users see only their own reports, admins see all
        if self.request.user.is_staff:
            return self.queryset
        return self.queryset.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def export(self, request, pk=None):
        report = self.get_object()
        # Export logic here
        return Response({'status': 'exporting'})
```

**4. Register URL** (`backend/config/urls.py`):
```python
from rest_framework.routers import DefaultRouter
from apps.reports.views import ReportViewSet

router = DefaultRouter()
router.register(r'reports', ReportViewSet, basename='report')

urlpatterns = [
    path('api/v1/', include(router.urls)),
    # ... other patterns
]
```

### Add Model Tests

**1. Create test file** (`backend/apps/reports/tests/test_models.py`):
```python
import pytest
from django.test import TestCase
from apps.users.factories import UserFactory
from apps.reports.models import Report

pytestmark = pytest.mark.django_db

class TestReportModel(TestCase):
    def setUp(self):
        self.user = UserFactory()
    
    def test_create_report(self):
        report = Report.objects.create(
            title='Test Report',
            user=self.user,
        )
        assert report.title == 'Test Report'
        assert report.user == self.user
```

**2. Create API tests** (`backend/apps/reports/tests/test_views.py`):
```python
import pytest
from rest_framework.test import APIClient
from apps.users.factories import UserFactory
from apps.reports.factories import ReportFactory

pytestmark = pytest.mark.django_db

class TestReportAPI:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)
    
    def test_list_reports(self):
        ReportFactory.create_batch(3, user=self.user)
        response = self.client.get('/api/v1/reports/')
        assert response.status_code == 200
        assert len(response.data['results']) == 3
```

### Run Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=apps --cov-report=html

# Run specific test file
pytest apps/reports/tests/test_models.py

# Run specific test
pytest apps/reports/tests/test_models.py::TestReportModel::test_create_report

# Run only unit tests (marked with @pytest.mark.unit)
pytest -m unit

# Stop on first failure
pytest -x

# Show print statements
pytest -s
```

### Database Migrations

```bash
cd backend

# Create migration
python manage.py makemigrations apps.reports

# Review migration
cat apps/reports/migrations/0001_initial.py

# Run migration
python manage.py migrate

# Revert to previous migration
python manage.py migrate apps.reports 0001

# Show migration history
python manage.py showmigrations
```

### Django Shell

```bash
cd backend
python manage.py shell

# Create test data
from apps.users.factories import UserFactory
user = UserFactory(email='test@example.com')

# Query data
from apps.reports.models import Report
reports = Report.objects.filter(user=user)

# Update data
report = reports.first()
report.title = 'Updated Title'
report.save()

# Delete data
report.delete()
```

### Using Enums for Constants

```python
# backend/apps/reports/enums/status.py
from enum import Enum

class ReportStatus(Enum):
    PENDING = 'PENDING'
    PROCESSING = 'PROCESSING'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'

# Use in model
from .enums import ReportStatus

class Report(models.Model):
    status = models.CharField(
        max_length=20,
        choices=[(s.value, s.name) for s in ReportStatus],
        default=ReportStatus.PENDING.value
    )

# Use in code
if report.status == ReportStatus.COMPLETED.value:
    # ...
```

---

## Troubleshooting

### Issue: "CORS error" when calling API from frontend

**Check:**
1. Backend is running on http://localhost:8000
2. Frontend is running on http://localhost:3000
3. CORS_ALLOWED_ORIGINS includes `http://localhost:3000`

**Fix:**
```env
# .env
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,localhost:3000
```

Restart backend after changing .env.

### Issue: "JWT token expired" error

**Fix:** Token should auto-refresh. If not:
1. Check token refresh endpoint is working: `POST /api/v1/auth/token/refresh/`
2. Check localStorage has `refresh_token`
3. Check Axios interceptor in `frontend/lib/api/client.ts`

### Issue: "Port 3000/8000 already in use"

```bash
# Find process using port 3000
lsof -i :3000

# Kill process
kill -9 <PID>

# Or use different port in Docker
# .env
FRONTEND_PORT=3001
BACKEND_PORT=8001

docker-compose down
docker-compose up -d --build
```

### Issue: Database connection error in Docker

```bash
# Reset everything
docker-compose down -v

# Rebuild from scratch
docker-compose up -d --build

# Check logs
docker-compose logs db
docker-compose logs backend
```

### Issue: Frontend can't connect to backend

**Check:**
- Backend is running: `http://localhost:8000/api/v1/schema/` should load
- NEXT_PUBLIC_API_URL is correct in `.env.local`
- Network tab in browser DevTools shows requests going to correct URL

**Common issue:** `.env.local` not being picked up
```bash
# Delete .next cache
rm -rf frontend/.next

# Restart dev server
npm run dev
```

### Issue: Tests failing with "ModuleNotFoundError"

```bash
cd backend

# Reinstall dependencies
pip install -r requirements/development.txt

# Clear pytest cache
pytest --cache-clear

# Run with verbose output
pytest -vv
```

### Issue: "IntegrityError" when creating test data

Ensure test fixtures/factories use correct defaults:
```python
# apps/reports/factories.py
from factory.django import DjangoModelFactory
from .models import Report

class ReportFactory(DjangoModelFactory):
    class Meta:
        model = Report
    
    title = factory.Faker('title')
    user = factory.SubFactory(UserFactory)
    data = {}  # Ensure default dict
```

---

## Environment Variables Cheatsheet

| Variable | Location | Purpose | Example |
|----------|----------|---------|---------|
| NEXT_PUBLIC_API_URL | frontend/.env.local | Frontend API URL | http://localhost:8000/api/v1 |
| DJANGO_SECRET_KEY | .env | Django secret key | (generate with openssl rand -base64 32) |
| DJANGO_DEBUG | .env | Debug mode | False (production), True (local dev) |
| DATABASE_URL | .env | Database connection | postgresql://postgres:password@db:5432/dbname |
| CORS_ALLOWED_ORIGINS | .env | Allowed origins | http://localhost:3000 |
| JWT_ACCESS_TOKEN_LIFETIME | .env | Token lifetime in minutes | 60 |

---

## Testing Workflow

### Before committing:

```bash
# Backend
cd backend
pytest -v --cov=apps  # Ensure all tests pass
python manage.py check  # Ensure no issues

# Frontend
cd frontend
npm run lint  # Check code quality
npm run build  # Ensure builds successfully

# Git
git status
git diff
git add .
git commit -m "feat: your message"
git push
```

---

## Performance Tips

### Backend
- Always use `select_related()` for ForeignKey
- Use `prefetch_related()` for M2M and reverse FK
- Add database indexes for frequently filtered fields
- Use `only()` to limit fields in queries
- Use pagination (page_size=20)

### Frontend
- Use React.memo() for expensive components
- Implement virtualization for long lists
- Cache API responses when appropriate
- Lazy load routes with dynamic imports
- Optimize images

---

## Documentation Links

- **Main README:** `/Users/gerwin/Developer/_personal/user-voucher-django-next/README.md`
- **API Docs:** http://localhost:8000/api/docs/ (Swagger)
- **Architecture:** `ARCHITECTURE.md` in project root
- **Backend Details:** `backend/API_SETUP.md`
- **Frontend Details:** `frontend/README.md`
- **Docker Guide:** `docs/DOCKER.md`

---

## Quick Command Reference

```bash
# Development Servers
npm run dev           # Frontend dev (port 3000)
python manage.py runserver  # Backend dev (port 8000)

# Build & Deploy
npm run build         # Frontend production build
docker-compose up -d --build  # Deploy with Docker

# Database
python manage.py migrate           # Run migrations
python manage.py createsuperuser   # Create admin
python manage.py shell             # Django shell

# Testing
pytest                             # Run all tests
pytest --cov=apps                  # With coverage
npm test                           # Frontend tests

# Code Quality
pytest --lf                        # Last failed
python -m black apps/              # Format backend
npm run lint                       # Lint frontend

# Docker
docker-compose logs -f             # View all logs
docker-compose ps                  # Service status
docker-compose exec backend bash   # Backend shell
docker-compose down -v             # Clean everything
```

---

**Last Updated:** November 7, 2025
**Project:** User Voucher Django Next.js
