# TPC Attendance Dashboard Setup Guide for Ubuntu Server

## Prerequisites

Before deploying on Ubuntu server, ensure you have:
- Ubuntu 18.04 LTS or newer
- Python 3.8+
- PostgreSQL (for production)
- Redis
- Git
- `sudo` access

## Quick Setup

### 1. Install System Dependencies

```bash
sudo apt-get update
sudo apt-get install -y python3-dev python3-venv postgresql postgresql-contrib redis-server nginx supervisor
```

### 2. Clone and Setup Project

```bash
# Clone the repository
cd /var/www
sudo git clone <your-repo-url> tpc_attendance_dashboard
sudo chown -R $(whoami):$(whoami) tpc_attendance_dashboard
cd tpc_attendance_dashboard

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Database Setup (PostgreSQL)

```bash
# Create database and user
sudo -u postgres psql

postgres=# CREATE DATABASE attendance_db;
postgres=# CREATE USER attendance_user WITH PASSWORD 'your_secure_password';
postgres=# ALTER ROLE attendance_user SET client_encoding TO 'utf8';
postgres=# ALTER ROLE attendance_user SET default_transaction_isolation TO 'read committed';
postgres=# ALTER ROLE attendance_user SET default_transaction_deferrable TO on;
postgres=# ALTER ROLE attendance_user SET timezone TO 'UTC';
postgres=# GRANT ALL PRIVILEGES ON DATABASE attendance_db TO attendance_user;
postgres=# \q
```

### 4. Update Environment Configuration

Edit `.env` file with your production settings:

```bash
nano .env
```

Key settings for production:
- `DEBUG=False`
- `SECRET_KEY=<generate-secure-key>` (Use: `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`)
- `ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,ip.address`
- `DB_PASSWORD=<your_password_from_step_3>`

### 5. Test the Startup Script

#### Test Debug Mode (Local Testing)
```bash
./startup.sh debug
```
- Runs on `http://localhost:8000`
- Django development server with hot reload
- Good for development and testing

#### Test Live Mode (Production Simulation)
```bash
./startup.sh live
```
- Runs on `http://0.0.0.0:8000` with Gunicorn
- Production-ready configuration
- Multiple worker processes

## Systemd Service Setup (Auto-Start on Boot)

### 1. Copy Service File

```bash
sudo cp tpc-attendance.service /etc/systemd/system/
```

### 2. Edit Service File (if needed)

```bash
sudo nano /etc/systemd/system/tpc-attendance.service
```

Update the paths if different from `/var/www/tpc_attendance_dashboard`:
- `WorkingDirectory=/path/to/project`
- `ExecStart=/path/to/project/startup.sh live`

### 3. Enable the Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable tpc-attendance.service

# Start the service
sudo systemctl start tpc-attendance.service

# Check status
sudo systemctl status tpc-attendance.service
```

### 4. Monitor Service

```bash
# View real-time logs
sudo journalctl -u tpc-attendance.service -f

# View last 50 lines
sudo journalctl -u tpc-attendance.service -n 50

# View logs from specific time
sudo journalctl -u tpc-attendance.service --since "2024-01-29 10:00:00"
```

## Nginx Configuration (Reverse Proxy)

### 1. Create Nginx Config

```bash
sudo nano /etc/nginx/sites-available/tpc-attendance
```

Add this configuration:

```nginx
upstream gunicorn {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    client_max_body_size 20M;

    location / {
        proxy_pass http://gunicorn;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    location /static/ {
        alias /var/www/tpc_attendance_dashboard/staticfiles/;
    }

    location /media/ {
        alias /var/www/tpc_attendance_dashboard/media/;
    }
}
```

### 2. Enable Nginx Configuration

```bash
sudo ln -s /etc/nginx/sites-available/tpc-attendance /etc/nginx/sites-enabled/
sudo nginx -t  # Test configuration
sudo systemctl restart nginx
```

## SSL/HTTPS Setup (Let's Encrypt)

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Issue certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Set auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

## Startup Script Usage

### Debug Mode (Development/Testing)
```bash
./startup.sh debug
```
- Use for local testing before deployment
- Django's development server with auto-reload
- All debug features enabled
- Useful for development work

### Live Mode (Production)
```bash
./startup.sh live
```
- Use on production servers
- Starts Gunicorn WSGI server with multiple workers
- DEBUG=False in production
- Logs to `/logs/gunicorn_*.log`
- Suitable for systemd auto-startup

### Auto-Startup on Server Boot
```bash
# Service will automatically start in LIVE mode
sudo systemctl restart tpc-attendance.service

# Or for debugging
sudo systemctl restart tpc-attendance.service  # Check logs if issues
```

## What the Startup Script Does

Both modes automatically:
1. ✅ Create virtual environment if missing
2. ✅ Activate virtual environment
3. ✅ Install dependencies from `requirements.txt`
4. ✅ Create/configure `.env` file (mode-specific)
5. ✅ **Apply database migrations automatically**
6. ✅ Collect static files
7. ✅ Check and start Redis if needed
8. ✅ Start Celery worker
9. ✅ Start Celery beat scheduler
10. ✅ Start appropriate web server (Django dev server or Gunicorn)

## Logs Location

All logs are stored in the `logs/` directory:

```
logs/
├── celery.log          # Celery worker logs
├── celery_beat.log     # Celery beat scheduler logs
├── gunicorn.log        # Gunicorn combined logs (live mode)
├── gunicorn_access.log # HTTP access logs (live mode)
└── gunicorn_error.log  # HTTP error logs (live mode)
```

View logs:
```bash
tail -f logs/gunicorn.log
tail -f logs/celery.log
```

## Common Commands

```bash
# Start the service
sudo systemctl start tpc-attendance.service

# Stop the service
sudo systemctl stop tpc-attendance.service

# Restart the service
sudo systemctl restart tpc-attendance.service

# Check service status
sudo systemctl status tpc-attendance.service

# View service logs
sudo journalctl -u tpc-attendance.service -f

# Enable auto-start on boot
sudo systemctl enable tpc-attendance.service

# Disable auto-start on boot
sudo systemctl disable tpc-attendance.service

# Run migrations manually
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

## Troubleshooting

### Service won't start
```bash
# Check detailed error logs
sudo journalctl -u tpc-attendance.service -n 50 --no-pager

# Test startup script manually
cd /var/www/tpc_attendance_dashboard
./startup.sh live
```

### Port 8000 already in use
```bash
# Find process using port 8000
sudo lsof -i :8000

# Kill the process
sudo kill -9 <PID>
```

### Database migration errors
```bash
# Run migrations manually with verbose output
python manage.py migrate --verbosity 3

# Check database connection
python manage.py dbshell
```

### Redis connection issues
```bash
# Check if Redis is running
redis-cli ping

# Start Redis
redis-server --daemonize yes

# Check Redis logs
tail -f /var/log/redis/redis-server.log
```

### Permission denied errors
```bash
# Fix ownership
sudo chown -R www-data:www-data /var/www/tpc_attendance_dashboard

# Fix permissions
chmod +x /var/www/tpc_attendance_dashboard/startup.sh
```

## Performance Tuning

Edit `.env` or `startup.sh` to adjust:

```bash
# Number of Gunicorn worker processes (default: 4)
GUNICORN_WORKERS=4

# Number of threads per worker (default: 2)
GUNICORN_THREADS=2

# Max requests before worker restart (default: 1000)
GUNICORN_MAX_REQUESTS=1000
```

## Backup & Recovery

Before deploying:
```bash
# Backup database
pg_dump -U attendance_user attendance_db > backup.sql

# Backup project files
tar -czf tpc_attendance_backup.tar.gz /var/www/tpc_attendance_dashboard
```

Recovery:
```bash
# Restore database
psql -U attendance_user attendance_db < backup.sql

# Restore files
tar -xzf tpc_attendance_backup.tar.gz -C /var/www
```

## Support

For issues or questions:
1. Check logs: `sudo journalctl -u tpc-attendance.service -f`
2. Test startup script: `./startup.sh live`
3. Review `.env` configuration
4. Ensure all dependencies are installed: `pip install -r requirements.txt`
