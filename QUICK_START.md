# MediScan Quick Start Guide

## Overview
MediScan AI is now fully configured with DevOps tools following Software Construction best practices. The app is ready to run with Docker.

## What Has Been Done

### 1. Backend Viewer Script
- **File**: `backend-view.bat`
- **Purpose**: View backend logs directly from terminal
- **Usage**: Double-click to run backend with full log output

### 2. Backend Connectivity Fixes
- Updated `backend/main.py` to use environment variables for host/port binding
- Backend now binds to `FLASK_RUN_HOST` (default: 127.0.0.1) and `FLASK_RUN_PORT` (default: 8000)
- This ensures Docker compatibility while maintaining local development support

### 3. Docker Configuration
- Updated `docker-compose.yml` with:
  - Custom network (mediscan-network)
  - Health checks for both services
  - Proper environment variables
  - Service dependencies with health conditions
- Backend Dockerfile includes health checks
- Frontend Dockerfile includes health checks

### 4. Frontend Auto-Detection
- Updated `mediscan-ai.html` to auto-detect backend URL
- Works in both local (127.0.0.1:8000) and Docker (localhost:8000) environments
- No manual configuration needed

### 5. Testing Script
- **File**: `test-backend.bat`
- **Purpose**: Test backend endpoints
- **Tests**: Health, registration, login endpoints

### 6. Documentation
- **DOCKER.md**: Complete Docker setup guide
- **SOFTWARE_CONSTRUCTION.md**: How app follows software construction principles
- **DEVOPS.md**: DevOps tools and practices guide

## How to Run the App

### Option 1: Docker (Recommended - Maximum Functionality)

1. **Install Docker Desktop** (if not already installed)
   - Download from https://www.docker.com/products/docker-desktop
   - Install and start Docker Desktop

2. **Start the application**
```bash
cd c:\Users\BANVEN\Desktop\mediscan
docker compose up --build
```

3. **Access the application**
- Frontend: http://localhost
- Backend Health: http://localhost:8000/health
- Backend API: http://localhost:8000

4. **Stop the application**
```bash
docker compose down
```

### Option 2: Local Development

1. **Start with the provided script**
- Double-click `run-mediscan.bat`

2. **Or start backend only**
- Double-click `backend-view.bat`

3. **Access the application**
- Frontend: http://127.0.0.1:5500/mediscan-ai.html
- Backend Health: http://127.0.0.1:8000/health
- Backend API: http://127.0.0.1:8000

## Account & Symptom Analysis

### Account Setup
1. Open the application in your browser
2. You will see a "Sign in to continue" banner
3. Register with any email and password (min 6 characters)
4. Login with your credentials

### Symptom Analysis
1. After logging in, describe your symptoms in the text area
2. Select age group, biological sex, duration (optional)
3. Adjust pain/discomfort level (optional)
4. Click "Analyse My Symptoms"
5. View results including:
   - Triage level (Home Care / See Doctor / Emergency)
   - Possible conditions with confidence scores
   - Recommended next steps
   - Warning signs
   - Follow-up questions

## Troubleshooting

### Backend Not Reachable
1. Check if backend is running:
   - Local: http://127.0.0.1:8000/health
   - Docker: http://localhost:8000/health
2. If not responding:
   - Local: Run `backend-view.bat`
   - Docker: Run `docker compose up --build`

### Account Not Showing
1. Ensure backend is running
2. Check browser console for errors (F12)
3. Verify you're logged in (check localStorage for token)
4. Try registering a new account

### Symptoms Not Analyzing
1. Ensure you're logged in
2. Check browser console for errors
3. Verify backend health endpoint is accessible
4. Check that ML models exist in `backend/models/`

### Docker Issues
1. Ensure Docker Desktop is running
2. Check for port conflicts (80, 8000)
3. View logs: `docker compose logs -f`
4. Rebuild: `docker compose up --build --force-recreate`

## DevOps Tools Integration

### Docker
- Containerized frontend and backend
- Multi-container orchestration with docker-compose
- Health checks for both services
- Custom networking

### AWS CloudWatch (Optional)
- Application logging to CloudWatch Logs
- Custom metrics for API requests, errors, response time
- Automatic alarm configuration
- Set AWS credentials in `.env` file to enable

### GitHub Actions (CI/CD)
- Automated testing
- Docker image building and pushing
- Security scanning with Trivy
- Deployment to production

### Git
- Version control with `.gitignore`
- Branching strategy support
- Change tracking

## Software Construction Principles Applied

Based on the Software Construction framework:

1. **Modularity**: Separate frontend and backend services
2. **Configuration Management**: Environment variables, .env files
3. **Security**: JWT authentication, password hashing, CORS
4. **Performance**: Health checks, caching, efficient queries
5. **Portability**: Docker-based, cross-platform
6. **Maintainability**: Clear documentation, code organization
7. **Observability**: Logging, metrics, health checks
8. **Quality**: Error handling, input validation, testing

## Next Steps

1. **Install Docker Desktop** (if not already installed)
2. **Run with Docker**: `docker compose up --build`
3. **Test functionality**: Register, login, analyze symptoms
4. **Configure AWS** (optional): Add AWS credentials for CloudWatch
5. **Set up CI/CD** (optional): Add GitHub secrets for automated deployment

## Support

For detailed information:
- Docker setup: See `DOCKER.md`
- DevOps practices: See `DEVOPS.md`
- Software construction: See `SOFTWARE_CONSTRUCTION.md`

## Summary

The MediScan app is now fully configured with:
- ✅ Backend viewer script for terminal access
- ✅ Fixed backend connectivity for Docker and local
- ✅ Enhanced Docker setup with health checks and networking
- ✅ Auto-detecting frontend for both environments
- ✅ Testing script for backend validation
- ✅ Comprehensive documentation
- ✅ Software construction best practices
- ✅ DevOps tools integration (Docker, AWS CloudWatch, GitHub Actions, Git)

**After installing Docker Desktop, you can run the entire application with a single command:**
```bash
docker compose up --build
```
