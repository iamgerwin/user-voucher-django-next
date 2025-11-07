# VPS Deployment Guide

This guide covers deploying the User Voucher System to a VPS (Virtual Private Server) using Docker Compose, with Nginx as a reverse proxy and Let's Encrypt for SSL certificates.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Server Setup](#server-setup)
- [Docker Installation](#docker-installation)
- [Application Deployment](#application-deployment)
- [Nginx Configuration](#nginx-configuration)
- [SSL Configuration](#ssl-configuration)
- [Monitoring and Maintenance](#monitoring-and-maintenance)
- [Troubleshooting](#troubleshooting)

## Prerequisites

- VPS with Ubuntu 22.04 LTS (recommended)
- Minimum 2GB RAM, 2 CPU cores
- Domain name pointed to your VPS IP
- SSH access to your server

## Server Setup

### 1. Initial Server Configuration

```bash
# SSH into your server
ssh root@your-server-ip

# Update system packages
apt update && apt upgrade -y

# Create a non-root user
adduser deployer
usermod -aG sudo deployer
usermod -aG docker deployer  # We'll install Docker next

# Configure firewall
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable

# Switch to deployer user
su - deployer
```

### 2. Install Essential Tools

```bash
sudo apt install -y \
    curl \
    git \
    vim \
    htop \
    build-essential
```

## Docker Installation

### Install Docker

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Log out and back in, or run:
newgrp docker

# Verify installation
docker --version
docker compose version
```

### Configure Docker

```bash
# Enable Docker to start on boot
sudo systemctl enable docker
sudo systemctl start docker

# Optional: Configure Docker logging
sudo tee /etc/docker/daemon.json > /dev/null <<EOF
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF

sudo systemctl restart docker
```

## Application Deployment

### 1. Clone Repository

```bash
# Create application directory
mkdir -p ~/apps
cd ~/apps

# Clone your repository
git clone <your-repository-url> user-voucher-django-next
cd user-voucher-django-next
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Generate Django secret key
openssl rand -base64 32

# Edit environment file
nano .env
```

**Important .env settings for production:**

```env
# Django
DJANGO_SECRET_KEY=<generated-secret-key>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://postgres:STRONG_PASSWORD@db:5432/voucher_system

# Redis
REDIS_PASSWORD=STRONG_PASSWORD
REDIS_URL=redis://:STRONG_PASSWORD@redis:6379/0

# CORS
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Next.js
NEXT_PUBLIC_API_URL=https://yourdomain.com/api/v1

# PostgreSQL
POSTGRES_PASSWORD=STRONG_PASSWORD

# Ports (if customizing)
BACKEND_PORT=8000
FRONTEND_PORT=3000

# Optional: Django superuser auto-creation
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@yourdomain.com
DJANGO_SUPERUSER_PASSWORD=STRONG_PASSWORD
```

### 3. Deploy Application

```bash
# Build and start services
docker compose up -d --build

# Check service status
docker compose ps

# View logs
docker compose logs -f

# Create superuser manually (if not auto-created)
docker compose exec backend python manage.py createsuperuser
```

### 4. Verify Deployment

```bash
# Test backend
curl http://localhost:8000/api/v1/health/

# Test frontend
curl http://localhost:3000
```

## Nginx Configuration

### 1. Install Nginx

```bash
sudo apt install -y nginx
```

### 2. Create Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/user-voucher-system
```

**Basic configuration (HTTP only):**

```nginx
upstream backend {
    server localhost:8000;
}

upstream frontend {
    server localhost:3000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    client_max_body_size 10M;

    # Frontend (Next.js)
    location / {
        proxy_pass http://frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Django Admin
    location /admin/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files (Django)
    location /static/ {
        alias /home/deployer/apps/user-voucher-django-next/backend/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files (Django)
    location /media/ {
        alias /home/deployer/apps/user-voucher-django-next/backend/media/;
        expires 7d;
    }
}
```

### 3. Enable Site

```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/user-voucher-system /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

## SSL Configuration

### 1. Install Certbot

```bash
sudo apt install -y certbot python3-certbot-nginx
```

### 2. Obtain SSL Certificate

```bash
# Obtain and configure SSL
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Follow prompts:
# - Enter email address
# - Agree to terms
# - Choose to redirect HTTP to HTTPS (option 2)
```

### 3. Test SSL Auto-Renewal

```bash
# Dry run
sudo certbot renew --dry-run

# Certbot will automatically renew certificates before expiry
```

### 4. Updated Nginx Configuration (with SSL)

After running Certbot, your configuration will be updated automatically. Verify it includes:

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # ... rest of configuration
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

## Monitoring and Maintenance

### Health Checks

```bash
# Check all services
docker compose ps

# Check specific service
docker compose exec backend python manage.py check

# View logs
docker compose logs backend
docker compose logs frontend

# Follow logs in real-time
docker compose logs -f
```

### Database Backup

```bash
# Create backup directory
mkdir -p ~/backups

# Backup PostgreSQL database
docker compose exec db pg_dump -U postgres voucher_system > ~/backups/backup_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup
docker compose exec -T db psql -U postgres voucher_system < ~/backups/backup_20240101_120000.sql
```

### Automated Backups

```bash
# Create backup script
cat > ~/backup-db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR=~/backups
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$DATE.sql"

# Create backup
cd ~/apps/user-voucher-django-next
docker compose exec -T db pg_dump -U postgres voucher_system > $BACKUP_FILE

# Compress
gzip $BACKUP_FILE

# Remove backups older than 7 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_FILE.gz"
EOF

chmod +x ~/backup-db.sh

# Add to crontab (daily at 2 AM)
crontab -e
# Add line:
# 0 2 * * * /home/deployer/backup-db.sh
```

### Log Rotation

Docker automatically handles log rotation if configured in `/etc/docker/daemon.json`.

### System Updates

```bash
# Update application
cd ~/apps/user-voucher-django-next
git pull origin main
docker compose up -d --build

# Update system packages
sudo apt update && sudo apt upgrade -y

# Clean up old Docker resources
docker system prune -a
```

### Monitoring

**Install monitoring tools:**

```bash
# Install htop for system monitoring
sudo apt install -y htop

# Install docker stats
watch docker stats

# Optional: Install Portainer for Docker management
docker run -d -p 9000:9000 \
  --name portainer --restart=always \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v portainer_data:/data \
  portainer/portainer-ce:latest
```

## Troubleshooting

### Service Won't Start

```bash
# Check service logs
docker compose logs backend
docker compose logs frontend

# Check individual container
docker compose exec backend bash
# Inside container:
python manage.py check
```

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker compose ps db

# Test database connection
docker compose exec db psql -U postgres -d voucher_system -c "SELECT 1;"

# Check logs
docker compose logs db
```

### Permission Issues

```bash
# Fix file permissions
cd ~/apps/user-voucher-django-next
sudo chown -R deployer:deployer .

# Fix static files
docker compose exec backend python manage.py collectstatic --noinput
```

### SSL Certificate Issues

```bash
# Check certificate status
sudo certbot certificates

# Renew manually
sudo certbot renew --nginx

# Test renewal
sudo certbot renew --dry-run
```

### High Memory Usage

```bash
# Check memory usage
free -h
docker stats

# Restart services
docker compose restart

# Adjust Docker resources if needed
# Edit docker-compose.yml to add resource limits
```

### Nginx Issues

```bash
# Check Nginx status
sudo systemctl status nginx

# Test configuration
sudo nginx -t

# View error logs
sudo tail -f /var/log/nginx/error.log
```

## Security Checklist

- [ ] Change all default passwords
- [ ] Configure firewall (UFW)
- [ ] Enable SSL/HTTPS
- [ ] Set `DJANGO_DEBUG=False`
- [ ] Use strong passwords for PostgreSQL and Redis
- [ ] Limit SSH access (disable password auth, use keys)
- [ ] Set up automated backups
- [ ] Configure fail2ban for SSH protection
- [ ] Keep system and Docker updated
- [ ] Monitor logs regularly
- [ ] Set up uptime monitoring
- [ ] Configure resource limits in docker-compose

## Performance Optimization

### Database Optimization

```bash
# Inside PostgreSQL container
docker compose exec db psql -U postgres -d voucher_system

# Create indexes
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);
CREATE INDEX CONCURRENTLY idx_vouchers_code ON vouchers(code);
CREATE INDEX CONCURRENTLY idx_vouchers_status ON vouchers(status);
```

### Nginx Caching

Add to Nginx configuration:

```nginx
# Cache zone
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m max_size=100m inactive=60m use_temp_path=off;

# In location blocks
location /api/ {
    proxy_cache api_cache;
    proxy_cache_valid 200 5m;
    proxy_cache_use_stale error timeout http_500 http_502 http_503 http_504;
    # ... other proxy settings
}
```

### Docker Resource Limits

Add to `docker-compose.yml`:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

## Support

For issues or questions:
1. Check application logs
2. Review this documentation
3. Contact the development team

---

**Deployment completed! Your application should now be running at https://yourdomain.com**
