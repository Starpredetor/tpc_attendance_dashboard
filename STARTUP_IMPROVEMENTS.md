# Startup Script Enhancement Summary

## Overview
The startup script has been completely redesigned to support both development and production deployment modes with automatic migrations and systemd integration for Ubuntu server auto-startup.

## Key Improvements

### 1. **Two Operating Modes**

#### Debug Mode (`./startup.sh debug`)
- **Purpose**: Local development and testing
- **Server**: Django development server with hot-reload
- **Debug Setting**: `DEBUG=True`
- **Database**: SQLite (default) or PostgreSQL
- **When to use**: 
  - Local development
  - Feature testing
  - Debugging issues
  - Quick iteration

#### Live Mode (`./startup.sh live`)
- **Purpose**: Production deployment on Ubuntu server
- **Server**: Gunicorn WSGI (4 workers by default)
- **Debug Setting**: `DEBUG=False`
- **Database**: PostgreSQL (recommended)
- **When to use**:
  - Ubuntu server deployment
  - Systemd auto-startup
  - Production environment
  - Load-balanced scenarios

### 2. **Automatic Database Migrations**
- ✅ Migrations run automatically before server starts
- ✅ No manual `python manage.py migrate` needed
- ✅ Works in both debug and live modes
- ✅ Safe to run repeatedly (idempotent)

### 3. **Enhanced Environment Configuration**
- Mode-specific `.env` file generation
- **Debug mode**: SQLite configuration for easy local testing
- **Live mode**: PostgreSQL configuration with security warnings
- Automatic environment variable export
- SECRET_KEY validation for production mode

### 4. **Improved Startup Process**
Status indicators for each step:
- `[✓]` Success - green
- `[✗]` Error - red  
- `[!]` Warning - yellow
- `[*]` Info - blue

Automatic steps in order:
1. Virtual environment setup
2. Dependency installation
3. Environment configuration
4. **Database migrations**
5. Static files collection
6. Redis service check/start
7. Celery worker startup
8. Celery beat startup
9. Web server startup

### 5. **Ubuntu systemd Service File**
- **File**: `tpc-attendance.service`
- **Auto-start**: Runs on server boot
- **Mode**: Lives in production mode
- **User**: Runs as `www-data` (web server user)
- **Restart policy**: Auto-restarts on failure
- **Installation**: 
  ```bash
  sudo cp tpc-attendance.service /etc/systemd/system/
  sudo systemctl daemon-reload
  sudo systemctl enable tpc-attendance.service
  sudo systemctl start tpc-attendance.service
  ```

### 6. **Comprehensive Logging**
All logs organized in `logs/` directory:
- `celery.log` - Async task worker
- `celery_beat.log` - Task scheduler
- `gunicorn.log` - Web server logs (live mode)
- `gunicorn_access.log` - HTTP request logs
- `gunicorn_error.log` - HTTP error logs

### 7. **Better Error Handling**
- Clear error messages
- Validation checks at each step
- Proper exit codes for automation
- Redis auto-start if missing
- Graceful signal handling (Ctrl+C)

### 8. **Production Safety Features**
- Force `DEBUG=False` in live mode
- SECRET_KEY validation in production
- Multiple Gunicorn worker processes
- Configurable worker threads
- Request timeout settings
- Proper dependency installation

## File Structure

```
project_root/
├── startup.sh                 # Main startup script (enhanced)
├── tpc-attendance.service     # Systemd service file (NEW)
├── UBUNTU_SETUP.md           # Complete Ubuntu deployment guide (NEW)
├── STARTUP_REFERENCE.sh      # Quick reference guide (NEW)
└── .env                       # Generated automatically (mode-specific)
```

## Usage Examples

### Local Development
```bash
# Run in debug mode with hot-reload
./startup.sh debug

# Server runs on http://localhost:8000
# Migrations applied automatically
# Changes reload automatically
```

### Production Deployment
```bash
# First-time setup
./startup.sh live

# Test manually before systemd
# Then set up systemd for auto-start

# For auto-start on server boot
sudo cp tpc-attendance.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable tpc-attendance.service
sudo systemctl start tpc-attendance.service
```

### Monitor Production Service
```bash
# Check service status
sudo systemctl status tpc-attendance.service

# View real-time logs
sudo journalctl -u tpc-attendance.service -f

# Restart service
sudo systemctl restart tpc-attendance.service

# View last 50 log lines
sudo journalctl -u tpc-attendance.service -n 50
```

## Configuration

### Environment Variables (.env)

**Debug Mode** (`./startup.sh debug`)
```
DEBUG=True
SECRET_KEY=dev-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
DB_ENGINE=django.db.backends.sqlite3
REDIS_HOST=localhost
REDIS_PORT=6379
```

**Live Mode** (`./startup.sh live`)
```
DEBUG=False
SECRET_KEY=<generate-secure-random-key>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DB_ENGINE=django.db.backends.postgresql
DB_NAME=attendance_db
DB_USER=attendance_user
DB_PASSWORD=secure_password
GUNICORN_WORKERS=4
GUNICORN_THREADS=2
```

## Performance Tuning (Live Mode)

Edit `.env` to adjust:
```bash
# Number of worker processes (default: 4)
# Recommended: 2-4 per CPU core
GUNICORN_WORKERS=4

# Threads per worker (default: 2)
# Good for I/O-bound operations
GUNICORN_THREADS=2

# Max requests before worker restart (default: 1000)
# Prevents memory leaks, set to 0 to disable
GUNICORN_MAX_REQUESTS=1000
```

## Systemd Service Benefits

- ✅ Auto-start on server boot
- ✅ Automatic restart on crash
- ✅ Centralized logging (journalctl)
- ✅ Easy management (systemctl)
- ✅ Process supervision
- ✅ Resource limits
- ✅ Integration with system monitoring

## Migration Behavior

The `python manage.py migrate` command:
- Runs **automatically** before server starts
- Uses `--noinput` flag for non-interactive mode
- Safe to run multiple times (unchanged migrations are skipped)
- Works with both SQLite and PostgreSQL
- Stops startup if migrations fail

This means:
- ✅ No more manual migration steps
- ✅ Fresh deployments work immediately
- ✅ Schema updates applied automatically
- ✅ Consistent across development and production

## Troubleshooting

### "Port 8000 already in use"
```bash
# Find process
sudo lsof -i :8000

# Kill it
sudo kill -9 <PID>
```

### "Redis connection refused"
```bash
# Check if Redis is running
redis-cli ping

# Start Redis
redis-server --daemonize yes
```

### "Database migration errors"
```bash
# Run migrations with verbose output
python manage.py migrate --verbosity 3

# Test database connection
python manage.py dbshell
```

### "Service won't start"
```bash
# Check detailed logs
sudo journalctl -u tpc-attendance.service -n 100

# Test startup script manually
./startup.sh live
```

## Next Steps

1. **Update `.env`** with your actual configuration
2. **Test debug mode locally**: `./startup.sh debug`
3. **Test live mode**: `./startup.sh live`
4. **Set up on Ubuntu server**:
   ```bash
   sudo cp tpc-attendance.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable tpc-attendance.service
   sudo systemctl start tpc-attendance.service
   ```
5. **Configure Nginx** as reverse proxy (see UBUNTU_SETUP.md)
6. **Set up SSL/HTTPS** with Let's Encrypt

## Additional Resources

- **[UBUNTU_SETUP.md](UBUNTU_SETUP.md)** - Complete Ubuntu deployment guide with database setup, Nginx configuration, SSL setup
- **[STARTUP_REFERENCE.sh](STARTUP_REFERENCE.sh)** - Quick reference for common commands
- **[README.md](README.md)** - Project overview
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Additional deployment information

## Support

For questions or issues:
1. Check the startup logs: `tail -f logs/gunicorn.log`
2. Review UBUNTU_SETUP.md for detailed setup instructions
3. Run startup script manually to see detailed error messages
4. Check systemd logs: `sudo journalctl -u tpc-attendance.service -f`
