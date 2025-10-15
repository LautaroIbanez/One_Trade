# One Trade Decision App - Setup Script (PowerShell)
# This script sets up the development environment on Windows

param(
    [switch]$SkipDocker,
    [switch]$SkipBackend,
    [switch]$SkipFrontend
)

# Colors for output
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor $Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor $Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor $Red
}

Write-Status "Setting up One Trade Decision App..."

# Check if Docker is installed
if (-not $SkipDocker) {
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-Error "Docker is not installed. Please install Docker Desktop first."
        exit 1
    }

    # Check if Docker Compose is installed
    if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
        Write-Error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    }

    Write-Status "Docker and Docker Compose are installed."
}

# Check if Python is installed
if (-not $SkipBackend) {
    if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
        Write-Error "Python is not installed. Please install Python 3.11+ first."
        exit 1
    }

    Write-Status "Python is installed."
}

# Check if Node.js is installed
if (-not $SkipFrontend) {
    if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
        Write-Error "Node.js is not installed. Please install Node.js 18+ first."
        exit 1
    }

    Write-Status "Node.js is installed."
}

Write-Status "All required tools are installed."

# Create .env file if it doesn't exist
if (-not (Test-Path "backend\.env")) {
    Write-Status "Creating .env file..."
    Copy-Item "backend\env.example" "backend\.env"
    Write-Warning "Please review and update the .env file with your configuration."
}

# Start Docker services
if (-not $SkipDocker) {
    Write-Status "Starting Docker services..."
    docker-compose up -d postgres redis rabbitmq

    # Wait for services to be ready
    Write-Status "Waiting for services to be ready..."
    Start-Sleep -Seconds 10
}

# Setup backend
if (-not $SkipBackend) {
    Write-Status "Setting up backend..."
    Set-Location backend

    # Create virtual environment if it doesn't exist
    if (-not (Test-Path "venv")) {
        Write-Status "Creating Python virtual environment..."
        python -m venv venv
    }

    # Activate virtual environment
    Write-Status "Activating virtual environment..."
    & ".\venv\Scripts\Activate.ps1"

    # Install dependencies
    Write-Status "Installing Python dependencies..."
    pip install -r requirements.txt

    # Run database migrations
    Write-Status "Running database migrations..."
    alembic upgrade head

    Set-Location ..
}

# Setup frontend
if (-not $SkipFrontend) {
    Write-Status "Setting up frontend..."
    Set-Location frontend

    # Install dependencies
    Write-Status "Installing Node.js dependencies..."
    npm install

    Set-Location ..
}

Write-Status "Setup completed successfully!"
Write-Host ""
Write-Host "🎉 One Trade Decision App is ready!" -ForegroundColor $Green
Write-Host ""
Write-Host "To start the application:"
Write-Host "1. Backend: cd backend && .\venv\Scripts\Activate.ps1 && uvicorn main:app --reload"
Write-Host "2. Frontend: cd frontend && npm run dev"
Write-Host ""
Write-Host "Access the application:"
Write-Host "- Frontend: http://localhost:3000"
Write-Host "- Backend API: http://localhost:8000/docs"
Write-Host "- Database Admin: http://localhost:5050 (admin@onetrade.local / admin)"
Write-Host "- RabbitMQ Management: http://localhost:15672 (onetrade / onetrade_dev)"
Write-Host ""
Write-Warning "Don't forget to update your .env file with your actual configuration!"

