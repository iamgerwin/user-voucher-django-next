# Docker Quick Start Guide

Get the User Voucher System running with Docker in minutes!

## Prerequisites

- Docker (20.10+)
- Docker Compose (2.0+)

## Quick Start - Production Mode

```bash
# 1. Clone the repository (if not already done)
git clone <repository-url>
cd user-voucher-django-next

# 2. Create environment file
cp .env.example .env

# 3. Generate a secure secret key and update .env
openssl rand -base64 32
# Add the output to DJANGO_SECRET_KEY in .env

# 4. Build and start all services
docker-compose up -d --build

# 5. Check service status
docker-compose ps

# 6. View logs
docker-compose logs -f
```

Access the application:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/api/v1
- **Admin Panel**: http://localhost:8000/admin
- **API Docs**: http://localhost:8000/api/docs

## Quick Start - Development Mode

```bash
# 1. Start development environment
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build

# 2. View logs
docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs -f
```

Development features:
- Hot reload for both frontend and backend
- Debug ports exposed
- Source code mounted for live editing
- Development databases on different ports

## Common Commands

```bash
# Stop all services
docker-compose down

# Restart services
docker-compose restart

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Run Django commands
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py shell

# Access container shell
docker-compose exec backend bash
docker-compose exec frontend sh

# Clean up everything
docker-compose down -v
```

## Next Steps

For detailed documentation, see:
- [Complete Docker Documentation](docs/DOCKER.md)
- [Backend Setup](backend/QUICK_START.md)
- [Frontend README](frontend/README.md)

## Troubleshooting

### Port already in use
```bash
# Change ports in .env
BACKEND_PORT=8001
FRONTEND_PORT=3001
```

### Database connection failed
```bash
# Reset and recreate
docker-compose down -v
docker-compose up -d
```

### Permission denied
```bash
# Fix ownership
sudo chown -R $USER:$USER .
```

For more troubleshooting, see [docs/DOCKER.md](docs/DOCKER.md#troubleshooting).
