# 🚀 Development Guide - One Trade Decision App

This guide will help you set up and run the One Trade Decision App in development mode.

## 📋 Prerequisites

### Required Software

- **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux)
- **Python 3.11+** with pip
- **Node.js 18+** with npm
- **Git**

### Optional Tools

- **Postman** or **Insomnia** for API testing
- **VS Code** with recommended extensions
- **pgAdmin** for database management

## 🛠️ Quick Setup

### Option 1: Automated Setup (Recommended)

#### Windows (PowerShell)
```powershell
# Run the setup script
.\scripts\setup.ps1

# Or with specific options
.\scripts\setup.ps1 -SkipDocker  # Skip Docker setup
.\scripts\setup.ps1 -SkipBackend # Skip backend setup
.\scripts\setup.ps1 -SkipFrontend # Skip frontend setup
```

#### Linux/Mac (Bash)
```bash
# Make script executable
chmod +x scripts/setup.sh

# Run the setup script
./scripts/setup.sh
```

### Option 2: Manual Setup

#### 1. Environment Configuration

```bash
# Copy environment template
cp backend/env.example backend/.env

# Edit the .env file with your configuration
# At minimum, update the database passwords
```

#### 2. Start Infrastructure Services

```bash
# Start PostgreSQL, Redis, and RabbitMQ
docker-compose up -d postgres redis rabbitmq

# Wait for services to be ready (about 10 seconds)
```

#### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start the backend server
uvicorn main:app --reload
```

#### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

## 🌐 Access Points

Once everything is running, you can access:

- **Frontend Application**: http://localhost:3000
- **Backend API Documentation**: http://localhost:8000/docs
- **Backend API (ReDoc)**: http://localhost:8000/redoc
- **Database Admin (pgAdmin)**: http://localhost:5050
  - Email: `admin@onetrade.local`
  - Password: `admin`
- **RabbitMQ Management**: http://localhost:15672
  - Username: `onetrade`
  - Password: `onetrade_dev`

## 🗄️ Database Management

### Connection Details

- **Host**: localhost
- **Port**: 5432
- **Database**: onetrade
- **Username**: onetrade
- **Password**: onetrade_dev

### Useful Commands

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback to previous migration
alembic downgrade -1

# View migration history
alembic history

# Reset database (WARNING: This will delete all data)
docker-compose down -v
docker-compose up -d postgres
alembic upgrade head
```

## 🧪 Testing

### Backend Tests

```bash
cd backend

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate   # Windows

# Run all tests
pytest

# Run tests with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_recommendations.py

# Run tests with verbose output
pytest -v
```

### Frontend Tests

```bash
cd frontend

# Run unit tests
npm test

# Run tests with coverage
npm run test:coverage

# Run tests in watch mode
npm run test:watch
```

## 🔧 Development Workflow

### 1. Making Changes

1. **Backend Changes**:
   - Modify code in `backend/app/`
   - Create migrations if database changes are needed
   - Test your changes with pytest
   - The server will auto-reload on file changes

2. **Frontend Changes**:
   - Modify code in `frontend/src/`
   - The development server will auto-reload
   - Use React DevTools for debugging

### 2. Database Changes

1. Modify models in `backend/app/models/`
2. Create migration: `alembic revision --autogenerate -m "Description"`
3. Review the generated migration file
4. Apply migration: `alembic upgrade head`

### 3. API Development

1. Add new endpoints in `backend/app/api/v1/endpoints/`
2. Update schemas in `backend/app/schemas/`
3. Test endpoints using the interactive docs at http://localhost:8000/docs

## 🐛 Troubleshooting

### Common Issues

#### 1. Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Kill the process
kill -9 <PID>  # Linux/Mac
taskkill /PID <PID> /F  # Windows
```

#### 2. Database Connection Issues

```bash
# Check if PostgreSQL is running
docker-compose ps

# Restart PostgreSQL
docker-compose restart postgres

# Check logs
docker-compose logs postgres
```

#### 3. Python Virtual Environment Issues

```bash
# Remove and recreate virtual environment
rm -rf backend/venv  # Linux/Mac
rmdir /s backend\venv  # Windows

# Recreate
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

#### 4. Node.js Dependencies Issues

```bash
# Clear npm cache
npm cache clean --force

# Remove node_modules and reinstall
rm -rf node_modules package-lock.json  # Linux/Mac
rmdir /s node_modules & del package-lock.json  # Windows
npm install
```

### Getting Help

1. Check the logs:
   ```bash
   # Backend logs
   docker-compose logs backend
   
   # Database logs
   docker-compose logs postgres
   
   # Frontend logs (in terminal where npm run dev is running)
   ```

2. Verify all services are running:
   ```bash
   docker-compose ps
   ```

3. Check environment variables:
   ```bash
   # Verify .env file exists and has correct values
   cat backend/.env
   ```

## 📁 Project Structure

```
decision_app/
├── backend/                 # FastAPI backend
│   ├── app/                # Application code
│   │   ├── api/           # API routes
│   │   ├── core/          # Core functionality
│   │   ├── models/        # Database models
│   │   └── schemas/       # Pydantic schemas
│   ├── alembic/           # Database migrations
│   ├── tests/             # Backend tests
│   └── requirements.txt   # Python dependencies
├── frontend/               # React frontend
│   ├── src/               # Source code
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   └── lib/           # Utilities
│   └── package.json       # Node.js dependencies
├── scripts/               # Setup and utility scripts
├── docker-compose.yml     # Docker services
└── README.md             # This file
```

## 🚀 Next Steps

1. **Explore the API**: Visit http://localhost:8000/docs
2. **Check the Frontend**: Visit http://localhost:3000
3. **Read the Documentation**: Check the `docs/` folder
4. **Run Tests**: Ensure everything is working
5. **Start Developing**: Pick a task from the backlog

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Tailwind CSS Documentation](https://tailwindcss.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [TimescaleDB Documentation](https://docs.timescale.com/)

---

Happy coding! 🎉

