#!/bin/bash

##################################################################
# TPC Attendance Dashboard - Automatic Startup Script for Linux
# Supports two modes: debug (development) and live (production)
# Usage: ./startup.sh [debug|live]
# Example: ./startup.sh debug   # Development mode with hot reload
#          ./startup.sh live    # Production mode with gunicorn
##################################################################

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Default mode
MODE="${1:-debug}"

# Validate mode argument
if [[ "$MODE" != "debug" && "$MODE" != "live" ]]; then
    echo "Error: Invalid mode '$MODE'. Use 'debug' or 'live'"
    echo "Usage: $0 [debug|live]"
    exit 1
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}TPC Attendance Dashboard - Startup${NC}"
echo -e "${BLUE}Mode: ${MODE^^}${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Function to print status
print_status() {
    echo -e "${BLUE}[*]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Check if virtual environment exists
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    print_status "Virtual environment not found. Creating..."
    python3 -m venv "$SCRIPT_DIR/venv"
    if [ $? -ne 0 ]; then
        print_error "Failed to create virtual environment"
        exit 1
    fi
    print_success "Virtual environment created"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source "$SCRIPT_DIR/venv/bin/activate"

if [ $? -ne 0 ]; then
    print_error "Failed to activate virtual environment"
    exit 1
fi
print_success "Virtual environment activated"

# Install/upgrade dependencies
print_status "Installing dependencies from requirements.txt..."
pip install -q -r "$SCRIPT_DIR/requirements.txt"

if [ $? -ne 0 ]; then
    print_error "Failed to install dependencies"
    exit 1
fi
print_success "Dependencies installed"

# Check if .env file exists and load/create it based on mode
print_status "Checking environment configuration..."
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    print_warning "Creating .env file with default values..."
    if [ "$MODE" = "live" ]; then
        cat > "$SCRIPT_DIR/.env" << 'EOF'
# Django Settings (LIVE/PRODUCTION MODE)
DEBUG=False
SECRET_KEY=your-secret-key-change-this-in-production-DO-NOT-USE-DEFAULT
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Database (PostgreSQL - recommended for production)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=attendance_db
DB_USER=attendance_user
DB_PASSWORD=secure_password_here
DB_HOST=localhost
DB_PORT=5432

# Redis (for Celery & Caching)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True

# Server Configuration
GUNICORN_WORKERS=4
GUNICORN_THREADS=2
GUNICORN_MAX_REQUESTS=1000
EOF
    else
        cat > "$SCRIPT_DIR/.env" << 'EOF'
# Django Settings (DEBUG/DEVELOPMENT MODE)
DEBUG=True
SECRET_KEY=your-secret-key-change-this-in-production
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
CSRF_TRUSTED_ORIGINS=http://localhost,http://127.0.0.1

# Database (SQLite for development, PostgreSQL for production)
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
# DB_ENGINE=django.db.backends.postgresql
# DB_NAME=attendance_db
# DB_USER=attendance_user
# DB_PASSWORD=password123
# DB_HOST=localhost
# DB_PORT=5432

# Redis (for Celery & Caching)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
EOF
    fi
    print_success ".env file created - UPDATE with your settings before running in production"
else
    print_success ".env file found"
fi

# Export environment variables from .env
export $(cat "$SCRIPT_DIR/.env" | grep -v '#' | xargs)

# Validate critical environment variables
if [ "$MODE" = "live" ] && [ -z "$SECRET_KEY" ]; then
    print_error "SECRET_KEY is not set in .env file. Please update .env with a secure SECRET_KEY"
    exit 1
fi

# Change to project directory
cd "$SCRIPT_DIR"

# Run migrations
print_status "Running database migrations..."
python manage.py migrate --noinput

if [ $? -ne 0 ]; then
    print_error "Failed to run migrations"
    exit 1
fi
print_success "Migrations completed"

# Collect static files
print_status "Collecting static files..."
python manage.py collectstatic --noinput --clear 2>/dev/null

if [ $? -ne 0 ]; then
    print_warning "Failed to collect static files, but continuing..."
else
    print_success "Static files collected"
fi

# Check if Redis is running
print_status "Checking Redis connection..."
redis-cli ping > /dev/null 2>&1

if [ $? -ne 0 ]; then
    print_warning "Redis server is not running!"
    print_status "Starting Redis in the background..."
    redis-server --daemonize yes --port 6379
    sleep 2
    print_success "Redis started"
else
    print_success "Redis is running"
fi

# Create logs directory
mkdir -p "$SCRIPT_DIR/logs"

# Start Celery worker and beat
print_status "Starting Celery worker..."
celery -A tpc_attendance_dashboard worker -l info --logfile="$SCRIPT_DIR/logs/celery.log" &
CELERY_PID=$!
print_success "Celery worker started (PID: $CELERY_PID)"

print_status "Starting Celery beat (scheduler)..."
celery -A tpc_attendance_dashboard beat -l info --logfile="$SCRIPT_DIR/logs/celery_beat.log" &
BEAT_PID=$!
print_success "Celery beat started (PID: $BEAT_PID)"

# Give services time to start
sleep 2

# Cleanup function on exit
cleanup() {
    print_status "Shutting down services..."
    kill $CELERY_PID $BEAT_PID 2>/dev/null
    wait $CELERY_PID $BEAT_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

# Start the appropriate server based on mode
if [ "$MODE" = "debug" ]; then
    print_status "Configuration: DEBUG MODE"
    print_status "Starting Django Development Server..."
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Django Development Server${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo -e "${BLUE}Mode: DEBUG${NC}"
    echo -e "${BLUE}Server: http://0.0.0.0:8000${NC}"
    echo -e "${BLUE}Admin: http://0.0.0.0:8000/admin${NC}"
    echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    
    # Set DEBUG to True for development
    export DEBUG=True
    
    python manage.py runserver 0.0.0.0:8000
    
else
    # Live/Production mode with Gunicorn
    print_status "Configuration: LIVE MODE (Production)"
    print_status "Checking for Gunicorn..."
    
    # Check if gunicorn is installed
    pip list | grep -q gunicorn
    if [ $? -ne 0 ]; then
        print_status "Installing Gunicorn..."
        pip install -q gunicorn
        if [ $? -ne 0 ]; then
            print_error "Failed to install Gunicorn"
            kill $CELERY_PID $BEAT_PID 2>/dev/null
            exit 1
        fi
        print_success "Gunicorn installed"
    fi
    
    print_status "Starting Gunicorn WSGI server..."
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Gunicorn WSGI Server (Production)${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo -e "${BLUE}Mode: LIVE/PRODUCTION${NC}"
    echo -e "${BLUE}Server: 0.0.0.0:8000${NC}"
    echo -e "${BLUE}Workers: 4${NC}"
    echo -e "${BLUE}Log: $SCRIPT_DIR/logs/gunicorn.log${NC}"
    echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    
    # Set DEBUG to False for production
    export DEBUG=False
    
    # Get number of workers (2-4 per CPU core)
    WORKERS=${GUNICORN_WORKERS:-4}
    THREADS=${GUNICORN_THREADS:-2}
    
    # Run Gunicorn
    gunicorn \
        --bind 0.0.0.0:8000 \
        --workers $WORKERS \
        --threads $THREADS \
        --worker-class gthread \
        --max-requests 1000 \
        --timeout 60 \
        --access-logfile "$SCRIPT_DIR/logs/gunicorn_access.log" \
        --error-logfile "$SCRIPT_DIR/logs/gunicorn_error.log" \
        --log-level info \
        tpc_attendance_dashboard.wsgi:application
fi
