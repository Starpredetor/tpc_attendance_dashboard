#!/bin/bash

##################################################################
# TPC Attendance Dashboard - Automatic Startup Script for Linux
# This script will start the Django server and Celery workers
##################################################################

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}TPC Attendance Dashboard - Startup${NC}"
echo -e "${GREEN}========================================${NC}"

# Check if virtual environment exists
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
    python3 -m venv "$SCRIPT_DIR/venv"
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to create virtual environment${NC}"
        exit 1
    fi
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source "$SCRIPT_DIR/venv/bin/activate"

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to activate virtual environment${NC}"
    exit 1
fi

# Install/upgrade dependencies
echo -e "${YELLOW}Installing dependencies from requirements.txt...${NC}"
pip install -q -r "$SCRIPT_DIR/requirements.txt"

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to install dependencies${NC}"
    exit 1
fi

# Check if .env file exists
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo -e "${YELLOW}Creating .env file with default values...${NC}"
    cat > "$SCRIPT_DIR/.env" << 'EOF'
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-change-this-in-production
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
CSRF_TRUSTED_ORIGINS=http://localhost,http://127.0.0.1

# Database (PostgreSQL)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=attendance_db
DB_USER=attendance_user
DB_PASSWORD=password123
DB_HOST=localhost
DB_PORT=5432

# Redis (for Celery & Caching)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
EOF
    echo -e "${YELLOW}.env file created. Please update it with your settings.${NC}"
fi

# Run migrations
echo -e "${YELLOW}Running database migrations...${NC}"
cd "$SCRIPT_DIR"
python manage.py migrate --noinput

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to run migrations${NC}"
    exit 1
fi

# Collect static files
echo -e "${YELLOW}Collecting static files...${NC}"
python manage.py collectstatic --noinput --clear 2>/dev/null

# Check if Redis is running
echo -e "${YELLOW}Checking Redis connection...${NC}"
redis-cli ping > /dev/null 2>&1

if [ $? -ne 0 ]; then
    echo -e "${YELLOW}Warning: Redis server is not running!${NC}"
    echo -e "${YELLOW}Starting Redis in the background...${NC}"
    redis-server --daemonize yes --port 6379
    sleep 2
fi

# Create logs directory
mkdir -p "$SCRIPT_DIR/logs"

# Start Celery worker in background
echo -e "${YELLOW}Starting Celery worker...${NC}"
celery -A tpc_attendance_dashboard worker -l info --logfile="$SCRIPT_DIR/logs/celery.log" &
CELERY_PID=$!
echo -e "${GREEN}Celery worker started (PID: $CELERY_PID)${NC}"

# Start Celery beat in background
echo -e "${YELLOW}Starting Celery beat (scheduler)...${NC}"
celery -A tpc_attendance_dashboard beat -l info --logfile="$SCRIPT_DIR/logs/celery_beat.log" &
BEAT_PID=$!
echo -e "${GREEN}Celery beat started (PID: $BEAT_PID)${NC}"

# Give Celery time to start
sleep 2

# Start Django development server
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Starting Django Development Server${NC}"
echo -e "${GREEN}Server will be available at:${NC}"
echo -e "${GREEN}http://localhost:8000${NC}"
echo -e "${GREEN}Admin panel: http://localhost:8000/admin${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

python manage.py runserver 0.0.0.0:8000

# Cleanup on exit
trap "echo -e '${YELLOW}Shutting down...${NC}'; kill $CELERY_PID $BEAT_PID 2>/dev/null; exit" EXIT
