#!/bin/bash

# One Trade Decision App - Development Script
set -e

echo "🚀 Starting One Trade Decision App in development mode..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Run setup.sh first."
    exit 1
fi

# Start development services
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build


