# Docker Setup Guide

This guide covers the Docker setup for the User Voucher Django + Next.js application, including development and production environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Environment Variables](#environment-variables)
- [Quick Start](#quick-start)
- [Development Workflow](#development-workflow)
- [Production Deployment](#production-deployment)
- [Service Architecture](#service-architecture)
- [Common Commands](#common-commands)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

## Prerequisites

Before you begin, ensure you have the following installed:

- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher
- **Git**: For cloning the repository

Verify your installations:

```bash
docker --version
docker-compose --version
```

## Project Structure

```
user-voucher-django-next/
├── backend/
│   ├── Dockerfile              # Production Dockerfile
│   ├── Dockerfile.dev          # Development Dockerfile
│   ├── .dockerignore          # Files to exclude from build
│   ├── entrypoint.sh          # Container startup script
│   └── requirements/
│       ├── base.txt           # Base dependencies
│       ├── development.txt    # Development dependencies
│       └── production.txt     # Production dependencies
├── frontend/
│   ├── Dockerfile              # Production Dockerfile
│   ├── Dockerfile.dev          # Development Dockerfile
│   └── .dockerignore          # Files to exclude from build
├── docker-compose.yml          # Production configuration
├── docker-compose.dev.yml      # Development overrides
└── .env.example               # Environment variables template
```

## Environment Variables

Create a `.env` file in the root directory by copying the example:

```bash
cp .env.example .env
```

### Required Environment Variables

#### Django Backend

```env
# Django Configuration
DJANGO_SECRET_KEY=your-secret-key-here-generate-with-openssl-rand-base64-32
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
POSTGRES_DB=voucher_system
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# Redis Configuration
REDIS_PASSWORD=redis

# JWT Configuration
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440

# CORS Configuration
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

#### Next.js Frontend

```env
# Frontend Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

#### Optional: Superuser Creation

```env
# Superuser Configuration (optional)
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=secure_password_here
```

### Generating Secret Keys

Generate a secure Django secret key:

```bash
openssl rand -base64 32
```

## Quick Start

### Production Environment

1. **Build and start all services:**

```bash
docker-compose up -d --build
```

2. **Check service status:**

```bash
docker-compose ps
```

3. **View logs:**

```bash
docker-compose logs -f
```

4. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/api/v1
   - Admin Panel: http://localhost:8000/admin

5. **Stop services:**

```bash
docker-compose down
```

### Development Environment

1. **Build and start development services:**

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
```

2. **View logs:**

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs -f
```

3. **Stop services:**

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml down
```

## Development Workflow

### Hot Reload

The development setup supports hot reload for both frontend and backend:

- **Backend**: Code changes are automatically detected by Django's development server
- **Frontend**: Next.js development server watches for file changes

### Running Commands in Containers

#### Backend Commands

```bash
# Django shell
docker-compose exec backend python manage.py shell

# Create migrations
docker-compose exec backend python manage.py makemigrations

# Run migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Run tests
docker-compose exec backend pytest

# Collect static files
docker-compose exec backend python manage.py collectstatic --noinput
```

#### Frontend Commands

```bash
# Install new packages
docker-compose exec frontend npm install <package-name>

# Run linter
docker-compose exec frontend npm run lint

# Access shell
docker-compose exec frontend sh
```

#### Database Commands

```bash
# Access PostgreSQL shell
docker-compose exec db psql -U postgres -d voucher_system

# Create database backup
docker-compose exec db pg_dump -U postgres voucher_system > backup.sql

# Restore database backup
docker-compose exec -T db psql -U postgres voucher_system < backup.sql
```

#### Redis Commands

```bash
# Access Redis CLI
docker-compose exec redis redis-cli

# Clear Redis cache
docker-compose exec redis redis-cli FLUSHALL
```

### Development Tools (Optional)

Uncomment the following services in `docker-compose.dev.yml` to enable:

#### MailHog - Email Testing

Access web UI at http://localhost:8025

```yaml
mailhog:
  image: mailhog/mailhog:latest
  ports:
    - "1025:1025"  # SMTP
    - "8025:8025"  # Web UI
```

#### PgAdmin - Database Management

Access at http://localhost:5050

```yaml
pgadmin:
  image: dpage/pgadmin4:latest
  environment:
    PGADMIN_DEFAULT_EMAIL: admin@admin.com
    PGADMIN_DEFAULT_PASSWORD: admin
  ports:
    - "5050:80"
```

#### Redis Commander - Redis Management

Access at http://localhost:8081

```yaml
redis-commander:
  image: rediscommander/redis-commander:latest
  ports:
    - "8081:8081"
```

## Production Deployment

### Pre-deployment Checklist

1. **Security**:
   - [ ] Generate strong `DJANGO_SECRET_KEY`
   - [ ] Set `DJANGO_DEBUG=False`
   - [ ] Configure proper `DJANGO_ALLOWED_HOSTS`
   - [ ] Set strong database passwords
   - [ ] Configure Redis password
   - [ ] Review CORS settings

2. **Environment**:
   - [ ] Update `.env` file with production values
   - [ ] Configure proper domain names
   - [ ] Set up SSL/TLS certificates
   - [ ] Configure proper backup strategy

3. **Resources**:
   - [ ] Adjust worker counts in gunicorn command
   - [ ] Configure memory limits
   - [ ] Set up monitoring and logging

### Build Production Images

```bash
# Build all services
docker-compose build

# Build specific service
docker-compose build backend
docker-compose build frontend
```

### Deploy Services

```bash
# Start services
docker-compose up -d

# Check health
docker-compose ps

# View logs
docker-compose logs -f
```

### Scaling Services

```bash
# Scale backend workers
docker-compose up -d --scale backend=3

# Scale with specific configuration
docker-compose up -d --scale backend=3 --scale frontend=2
```

### Health Checks

All services include health checks:

- **PostgreSQL**: `pg_isready` check every 10s
- **Redis**: `redis-cli ping` every 10s
- **Backend**: HTTP check to `/api/v1/health/` every 30s
- **Frontend**: HTTP check to `/api/health` every 30s

## Service Architecture

### Network Configuration

All services run on the `voucher_network` bridge network, allowing them to communicate using service names:

- `db` - PostgreSQL database
- `redis` - Redis cache
- `backend` - Django API
- `frontend` - Next.js application

### Volume Mounts

#### Production Volumes

- `postgres_data`: PostgreSQL data persistence
- `redis_data`: Redis data persistence
- `backend/staticfiles`: Django static files
- `backend/mediafiles`: User uploaded files

#### Development Volumes

Additional volumes for hot reload:

- `./backend:/app`: Backend source code
- `./frontend:/app`: Frontend source code
- `backend_venv`: Python virtual environment

### Port Mapping

Default ports (configurable via environment variables):

- **Frontend**: 3000
- **Backend**: 8000
- **PostgreSQL**: 5432 (production), 5433 (development)
- **Redis**: 6379 (production), 6380 (development)

## Common Commands

### Container Management

```bash
# View running containers
docker-compose ps

# View all containers (including stopped)
docker-compose ps -a

# Start services
docker-compose start

# Stop services
docker-compose stop

# Restart services
docker-compose restart

# Remove containers
docker-compose down

# Remove containers and volumes
docker-compose down -v
```

### Logs and Monitoring

```bash
# View all logs
docker-compose logs

# Follow logs
docker-compose logs -f

# View specific service logs
docker-compose logs backend
docker-compose logs frontend

# View last 100 lines
docker-compose logs --tail=100 backend

# View logs with timestamps
docker-compose logs -t backend
```

### Image Management

```bash
# Build images
docker-compose build

# Build without cache
docker-compose build --no-cache

# Pull latest images
docker-compose pull

# List images
docker images

# Remove unused images
docker image prune

# Remove all unused images
docker image prune -a
```

### Volume Management

```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect voucher_postgres_data

# Remove volume
docker volume rm voucher_postgres_data

# Remove all unused volumes
docker volume prune
```

## Troubleshooting

### Common Issues

#### 1. Port Already in Use

**Error**: `Bind for 0.0.0.0:8000 failed: port is already allocated`

**Solution**:
```bash
# Find process using the port
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or change port in .env
BACKEND_PORT=8001
```

#### 2. Database Connection Failed

**Error**: `FATAL: password authentication failed`

**Solution**:
```bash
# Remove volumes and recreate
docker-compose down -v
docker-compose up -d

# Check database logs
docker-compose logs db
```

#### 3. Permission Denied

**Error**: `Permission denied` when accessing files

**Solution**:
```bash
# Fix ownership (run on host)
sudo chown -R $USER:$USER .

# Or adjust permissions in Dockerfile
RUN chown -R django:django /app
```

#### 4. Out of Memory

**Error**: Container crashes due to memory issues

**Solution**:
```bash
# Add memory limits in docker-compose.yml
services:
  backend:
    mem_limit: 512m
    memswap_limit: 1g
```

#### 5. Static Files Not Loading

**Solution**:
```bash
# Collect static files
docker-compose exec backend python manage.py collectstatic --noinput

# Check volume mounts
docker-compose exec backend ls -la /app/staticfiles
```

#### 6. Frontend Can't Connect to Backend

**Solution**:
```bash
# Check network connectivity
docker-compose exec frontend ping backend

# Verify NEXT_PUBLIC_API_URL in .env
# Should be http://localhost:8000/api/v1 for local development
```

### Debugging

#### Enter Container Shell

```bash
# Backend
docker-compose exec backend bash

# Frontend
docker-compose exec frontend sh

# Database
docker-compose exec db bash
```

#### Check Container Resources

```bash
# CPU and memory usage
docker stats

# Specific container
docker stats voucher_backend
```

#### Inspect Container

```bash
# View container details
docker inspect voucher_backend

# View network settings
docker inspect voucher_backend --format='{{.NetworkSettings.Networks}}'
```

### Reset Everything

```bash
# Stop all containers
docker-compose down

# Remove all volumes
docker-compose down -v

# Remove all images
docker-compose down --rmi all

# Clean system
docker system prune -a --volumes

# Rebuild from scratch
docker-compose up -d --build
```

## Best Practices

### Security

1. **Never commit `.env` files** - Use `.env.example` as template
2. **Use secrets management** in production (Docker Swarm secrets, Kubernetes secrets)
3. **Run containers as non-root** - Already configured in Dockerfiles
4. **Scan images for vulnerabilities**:
   ```bash
   docker scan voucher_backend
   ```
5. **Keep images updated**:
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

### Performance

1. **Use multi-stage builds** - Reduces image size (already implemented)
2. **Optimize layer caching** - Order Dockerfile commands by change frequency
3. **Use .dockerignore** - Exclude unnecessary files from build context
4. **Limit container resources**:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '1'
         memory: 512M
   ```

### Maintenance

1. **Regular backups**:
   ```bash
   # Backup database
   docker-compose exec db pg_dump -U postgres voucher_system > backup_$(date +%Y%m%d).sql

   # Backup volumes
   docker run --rm -v voucher_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz /data
   ```

2. **Monitor logs**:
   ```bash
   # Set up log rotation
   docker-compose logs --no-log-prefix > app.log
   ```

3. **Update dependencies**:
   ```bash
   # Rebuild with latest dependencies
   docker-compose build --no-cache
   docker-compose up -d
   ```

### Development

1. **Use development compose file** for local development
2. **Mount source code** for hot reload (already configured)
3. **Use environment-specific settings** (development.py vs production.py)
4. **Test in production mode** before deploying:
   ```bash
   docker-compose -f docker-compose.yml up -d
   ```

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Next.js Deployment](https://nextjs.org/docs/deployment)

## Support

For issues and questions:

1. Check logs: `docker-compose logs -f`
2. Review this documentation
3. Check Docker and service documentation
4. Create an issue in the project repository
