#!/bin/bash

# One Trade Decision App - Setup Script
# This script sets up the development environment

set -e

echo "🚀 Setting up One Trade Decision App..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js first."
    exit 1
fi

print_status "All required tools are installed."

# Create .env file if it doesn't exist
if [ ! -f backend/.env ]; then
    print_status "Creating .env file..."
    cp backend/env.example backend/.env
    print_warning "Please review and update the .env file with your configuration."
fi

# Start Docker services
print_status "Starting Docker services..."
docker-compose up -d postgres redis rabbitmq

# Wait for services to be ready
print_status "Waiting for services to be ready..."
sleep 10

# Setup backend
print_status "Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
print_status "Installing Python dependencies..."
pip install -r requirements.txt

# Run database migrations
print_status "Running database migrations..."
alembic upgrade head

# Setup frontend
print_status "Setting up frontend..."
cd ../frontend

# Install dependencies
print_status "Installing Node.js dependencies..."
npm install

cd ..

print_status "Setup completed successfully!"
echo ""
echo "🎉 One Trade Decision App is ready!"
echo ""
echo "To start the application:"
echo "1. Backend: cd backend && source venv/bin/activate && uvicorn main:app --reload"
echo "2. Frontend: cd frontend && npm run dev"
echo ""
echo "Access the application:"
echo "- Frontend: http://localhost:3000"
echo "- Backend API: http://localhost:8000/docs"
echo "- Database Admin: http://localhost:5050 (admin@onetrade.local / admin)"
echo "- RabbitMQ Management: http://localhost:15672 (onetrade / onetrade_dev)"
echo ""
print_warning "Don't forget to update your .env file with your actual configuration!"