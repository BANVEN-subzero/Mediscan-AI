# MediScan Docker Setup Guide

This guide covers the Docker setup for MediScan, following software construction best practices.

## Prerequisites

- Docker Desktop installed and running
- (Optional) AWS credentials for CloudWatch monitoring

## Quick Start

### Using Docker Compose (Recommended)

1. **Start the application:**
```bash
docker compose up --build
```

2. **Access the application:**
- Frontend: http://localhost
- Backend Health: http://localhost:8000/health
- Backend API: http://localhost:8000

3. **Stop the application:**
```bash
docker compose down
```

### Using Docker Commands

**Build images:**
```bash
docker build -t mediscan-backend ./backend
docker build -t mediscan-frontend .
```

**Run containers:**
```bash
docker run -d -p 8000:8000 --name mediscan-backend mediscan-backend
docker run -d -p 80:80 --name mediscan-frontend mediscan-frontend
```

## Architecture

### Services

1. **Backend Service**
- Base image: python:3.11-slim
- Port: 8000
- Health check: /health endpoint
- Environment variables:
  - FLASK_ENV=production
  - FLASK_RUN_HOST=0.0.0.0
  - FLASK_RUN_PORT=8000
  - JWT_SECRET_KEY
  - ALLOWED_ORIGINS
  - AWS_* (optional, for CloudWatch)

2. **Frontend Service**
- Base image: nginx:alpine
- Port: 80
- Health check: HTTP availability
- Depends on: backend (with health check)

### Networking

- Custom bridge network: mediscan-network
- Services communicate within the network
- Frontend accesses backend via localhost:8000 (port mapping)

## Health Checks

### Backend Health Check
```bash
curl http://localhost:8000/health
```
Expected response: `{"ok": true}`

### Container Health Status
```bash
docker compose ps
```

## Environment Variables

Create a `.env` file in the project root:

```env
# JWT Configuration
JWT_SECRET_KEY=your-secret-key-here

# AWS CloudWatch (Optional)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
```

## Development vs Production

### Development Mode
- Use `run-mediscan.bat` for local development
- Backend runs on 127.0.0.1:8000
- Frontend runs on 127.0.0.1:5500

### Production Mode (Docker)
- Use `docker compose up`
- Backend runs on 0.0.0.0:8000 (accessible from outside container)
- Frontend runs on port 80

## Troubleshooting

### Container won't start
```bash
# Check logs
docker compose logs backend
docker compose logs frontend

# Rebuild
docker compose up --build --force-recreate
```

### Health check failing
```bash
# Check if backend is responding
docker compose exec backend curl http://localhost:8000/health

# Check backend logs
docker compose logs -f backend
```

### Port conflicts
- Ensure ports 80 and 8000 are not in use
- Modify port mappings in docker-compose.yml if needed

### Network issues
```bash
# Check network
docker network ls
docker network inspect mediscan_mediscan-network

# Recreate network
docker compose down
docker network prune
docker compose up
```

## Software Construction Best Practices

### 1. Modularity
- Separate frontend and backend services
- Each service has its own Dockerfile
- Clear separation of concerns

### 2. Configuration Management
- Environment variables for configuration
- .env.example for reference
- No hardcoded secrets

### 3. Health Monitoring
- Health checks for both services
- Automatic restart on failure
- Dependency management (frontend waits for backend)

### 4. Security
- Minimal base images (alpine, slim)
- No root user where possible
- Secrets via environment variables
- CORS configuration

### 5. Scalability
- Services can be scaled independently
- Network allows horizontal scaling
- Stateless design

### 6. Maintainability
- Clear documentation
- Version-controlled configuration
- Reproducible builds

## CI/CD Integration

The GitHub Actions workflow (`.github/workflows/ci-cd.yml`) includes:
- Building Docker images
- Pushing to Docker Hub
- Security scanning with Trivy
- Deployment to production

## Monitoring

### Logs
```bash
# View all logs
docker compose logs -f

# View specific service logs
docker compose logs -f backend
docker compose logs -f frontend
```

### Metrics (CloudWatch)
If AWS credentials are configured:
- Application logs sent to CloudWatch Logs
- Custom metrics for API requests, errors, response time
- Alarms for high error rates and slow responses

## Performance Optimization

### Image Size
- Use multi-stage builds (can be implemented)
- Remove unnecessary dependencies
- Use .dockerignore files

### Resource Limits
Add to docker-compose.yml:
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
```

## Backup and Recovery

### Database Backup
```bash
# Copy SQLite database from container
docker cp mediscan-backend:/app/mediscan.db ./backup.db
```

### Volume Mounts
For persistent data, add volumes:
```yaml
services:
  backend:
    volumes:
      - ./backend/data:/app/data
```

## Next Steps

1. Set up AWS credentials for CloudWatch monitoring
2. Configure GitHub secrets for CI/CD
3. Set up production deployment (ECS, Kubernetes, etc.)
4. Implement automated testing in CI/CD
5. Add performance monitoring (APM tools)

## Support

For issues:
1. Check Docker Desktop is running
2. Verify no port conflicts
3. Review container logs
4. Check network connectivity
5. Consult DEVOPS.md for general DevOps guidance
