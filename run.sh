#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored messages
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a port is in use
port_in_use() {
    lsof -ti:$1 >/dev/null 2>&1
}

# Function to kill process on a port
kill_port() {
    if port_in_use $1; then
        print_warning "Port $1 is in use. Killing existing process..."
        lsof -ti:$1 | xargs kill -9 2>/dev/null
        sleep 1
    fi
}

# Function to cleanup on exit
cleanup() {
    print_info "Shutting down services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

# Trap Ctrl+C and call cleanup
trap cleanup INT TERM

# Check prerequisites
print_info "Checking prerequisites..."

if ! command_exists python3; then
    print_error "Python 3 is not installed. Please install Python 3.12+"
    exit 1
fi

if ! command_exists node; then
    print_error "Node.js is not installed. Please install Node.js 20+"
    exit 1
fi

if ! command_exists npm; then
    print_error "npm is not installed. Please install npm"
    exit 1
fi

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

print_info "Project directory: $SCRIPT_DIR"

# Check if .env exists
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    print_warning ".env file not found. Copying from .env.example..."
    cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
    print_info "Please review and update .env file if needed"
fi

# Backend setup
print_info "Setting up backend..."

cd "$BACKEND_DIR" || exit 1

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_info "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
print_info "Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if [ ! -f "venv/bin/django-admin" ]; then
    print_info "Installing backend dependencies..."
    pip install -q -r requirements/development.txt
fi

# Run migrations if needed
print_info "Checking database migrations..."
export DJANGO_SETTINGS_MODULE=config.settings.development
python manage.py migrate --noinput

# Kill existing backend process if any
kill_port 8000

# Start backend server
print_info "Starting Django backend on http://127.0.0.1:8000..."
python manage.py runserver > /dev/null 2>&1 &
BACKEND_PID=$!

# Wait for backend to start
sleep 2

if ! ps -p $BACKEND_PID > /dev/null; then
    print_error "Failed to start backend server"
    exit 1
fi

print_info "Backend started successfully (PID: $BACKEND_PID)"

# Frontend setup
print_info "Setting up frontend..."

cd "$FRONTEND_DIR" || exit 1

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    print_info "Installing frontend dependencies..."
    npm install
fi

# Remove lock file if exists
rm -f .next/dev/lock

# Kill existing frontend process if any
kill_port 3000

# Start frontend server
print_info "Starting Next.js frontend on http://localhost:3000..."
npm run dev > /dev/null 2>&1 &
FRONTEND_PID=$!

# Wait for frontend to start
sleep 3

if ! ps -p $FRONTEND_PID > /dev/null; then
    print_error "Failed to start frontend server"
    kill $BACKEND_PID
    exit 1
fi

print_info "Frontend started successfully (PID: $FRONTEND_PID)"

# Print summary
echo ""
echo "=========================================="
echo -e "${GREEN}✓ All services are running!${NC}"
echo "=========================================="
echo ""
echo "Backend (Django):"
echo "  - API:          http://127.0.0.1:8000"
echo "  - API Docs:     http://127.0.0.1:8000/api/docs/"
echo "  - Admin:        http://127.0.0.1:8000/admin"
echo ""
echo "Frontend (Next.js):"
echo "  - Application:  http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"
echo "=========================================="
echo ""

# Wait for processes
wait
