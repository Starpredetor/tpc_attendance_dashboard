# TPC Attendance Dashboard - Deployment Guide

## Database Migration

After pulling the latest changes, run these commands to apply database schema updates:

```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

## Important Changes

### 1. Security Improvements
- Moved SECRET_KEY and sensitive data to environment variables
- Added security headers for production
- Email configuration now uses environment variables

### 2. Performance Optimizations
- Added database indexes on frequently queried fields
- Optimized N+1 query problems with select_related/prefetch_related
- Implemented bulk operations for attendance marking
- Added Redis caching support

### 3. Celery Configuration
- Fixed Celery task naming and configuration
- Added proper Celery app initialization
- Updated requirements.txt with celery and redis packages

### 4. Code Quality
- Fixed duplicate audit log entries
- Improved error handling and messages
- Added proper validation and data sanitization
- Removed unreachable code

## New Dependencies

Install new dependencies:
```powershell
pip install -r requirements.txt
```

New packages added:
- celery==5.4.0
- redis==5.2.1

## Environment Variables

Create a `.env` file based on `.env.example`:
```powershell
cp .env.example .env
```

Then edit `.env` with your actual values.

## Redis Setup (Required for Celery & Caching)

### Windows:
1. Download Redis from: https://github.com/microsoftarchive/redis/releases
2. Install and start Redis service
3. Verify: `redis-cli ping` (should return "PONG")

### Or use Docker:
```powershell
docker run -d -p 6379:6379 redis:latest
```

## Running Celery

Start Celery worker (in separate terminal):
```powershell
celery -A tpc_attendance_dashboard worker -l info
```

Start Celery beat (for scheduled tasks):
```powershell
celery -A tpc_attendance_dashboard beat -l info
```

## Production Checklist

Before deploying to production:

1. Set `DEBUG=False` in .env
2. Generate a new SECRET_KEY
3. Update ALLOWED_HOSTS with your domain
4. Update CSRF_TRUSTED_ORIGINS with your domain URLs
5. Configure proper email credentials
6. Set up PostgreSQL database
7. Set up Redis server
8. Run `python manage.py collectstatic`
9. Configure proper web server (nginx/apache)
10. Set up SSL certificates

## Model Changes Summary

Added indexes to:
- Student: roll_number, email, batch, is_active
- Lecture: date, batch, lecture_type
- AttendanceRecord: lecture, student, status
- AuditLog: timestamp, action_type, actor

These indexes will significantly improve query performance.
