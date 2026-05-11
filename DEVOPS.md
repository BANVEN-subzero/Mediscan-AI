# MediScan DevOps Guide

This guide covers the DevOps tools and practices used in the MediScan project.

## Table of Contents

- [Git](#git)
- [Docker](#docker)
- [AWS CloudWatch](#aws-cloudwatch)
- [CI/CD Pipeline](#cicd-pipeline)
- [Environment Variables](#environment-variables)
- [Monitoring and Alerts](#monitoring-and-alerts)

## Git

### Repository Structure

The project uses Git for version control. The `.gitignore` file is configured to exclude:
- Python virtual environments (`.venv`, `venv`)
- Database files (`*.db`, `*.sqlite3`)
- ML model files (`*.pkl`)
- Environment variables (`.env`)
- Logs and temporary files

### Best Practices

1. **Commit messages**: Use clear, descriptive commit messages
2. **Branching**: Use feature branches for new work
3. **Pull requests**: Review code before merging to main/master

### Common Git Commands

```bash
# Check status
git status

# Add changes
git add .

# Commit changes
git commit -m "Description of changes"

# Push to remote
git push origin feature-branch

# Create a new branch
git checkout -b feature-name
```

## Docker

### Docker Compose

The project uses Docker Compose to orchestrate the frontend and backend services.

**Start the application:**
```bash
docker-compose up -d
```

**Stop the application:**
```bash
docker-compose down
```

**View logs:**
```bash
docker-compose logs -f
```

**Rebuild containers:**
```bash
docker-compose up -d --build
```

### Individual Services

**Backend:**
```bash
# Build backend image
docker build -t mediscan-backend ./backend

# Run backend container
docker run -p 8000:8000 mediscan-backend
```

**Frontend:**
```bash
# Build frontend image
docker build -t mediscan-frontend .

# Run frontend container
docker run -p 80:80 mediscan-frontend
```

### Health Checks

Both containers include health checks:

- **Backend**: Checks `/health` endpoint every 30 seconds
- **Frontend**: Checks HTTP availability every 30 seconds

View health status:
```bash
docker ps
```

## AWS CloudWatch

### Configuration

CloudWatch is configured via environment variables in `backend/.env`:

```env
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_REGION=us-east-1
```

### Features

#### 1. Logging

- Application logs are sent to CloudWatch Logs
- Log group: `MediScanLogs`
- Log stream: `FlaskBackend`

#### 2. Custom Metrics

The application tracks the following metrics:

- `APIRequest`: Count of API requests
- `APIRequestDuration`: Response time in seconds
- `APIRequestError`: Count of failed requests

#### 3. Alarms

Standard alarms are automatically configured:

- **High Error Rate**: Alerts when error rate exceeds 10 errors in 5 minutes
- **High Response Time**: Alerts when average response time exceeds 2 seconds
- **Low Request Rate**: Alerts when request rate drops below 1 request per hour

### Manual Metric Submission

You can manually submit custom metrics using the `CloudWatchMetrics` class:

```python
from cloudwatch_metrics import metrics

# Send a counter metric
metrics.put_counter("CustomMetric", 1)

# Send a gauge metric
metrics.put_gauge("CustomGauge", 42.5)
```

### Viewing Metrics in AWS Console

1. Go to AWS CloudWatch Console
2. Navigate to Metrics → Custom Namespaces
3. Select `MediScan` namespace
4. View your custom metrics and create dashboards

## CI/CD Pipeline

### GitHub Actions

The project uses GitHub Actions for continuous integration and deployment.

**Workflow file**: `.github/workflows/ci-cd.yml`

### Pipeline Stages

1. **Test**
   - Lints code with flake8
   - Runs tests with pytest
   - Uploads coverage reports

2. **Build and Push**
   - Builds Docker images
   - Pushes to Docker Hub
   - Tags images with branch and SHA

3. **Deploy**
   - Deploys to production environment
   - Notifies CloudWatch of deployment

4. **Security Scan**
   - Scans for vulnerabilities with Trivy
   - Uploads results to GitHub Security

### Required Secrets

Configure these secrets in your GitHub repository settings:

- `DOCKER_USERNAME`: Docker Hub username
- `DOCKER_PASSWORD`: Docker Hub password/access token
- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
- `AWS_REGION`: AWS region (e.g., `us-east-1`)

### Manual Workflow Trigger

You can manually trigger the workflow from the Actions tab in GitHub.

## Environment Variables

### Required Variables

Copy `backend/.env.example` to `backend/.env` and configure:

```env
# Flask Configuration
FLASK_ENV=production
ALLOWED_ORIGINS=*

# JWT Secret (change this in production!)
JWT_SECRET_KEY=your-random-secret-key

# AWS CloudWatch (optional, for monitoring)
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_REGION=us-east-1
```

### Using with Docker Compose

Set environment variables in `docker-compose.yml` or use a `.env` file:

```yaml
services:
  backend:
    environment:
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
```

## Monitoring and Alerts

### CloudWatch Dashboard

Create a CloudWatch dashboard to visualize:

- Request rate over time
- Response time trends
- Error rates
- Custom metrics

### Setting Up Notifications

Configure CloudWatch Alarms to send SNS notifications:

1. Create an SNS topic
2. Subscribe your email/phone to the topic
3. Configure alarms to use the SNS topic
4. You'll receive alerts when thresholds are breached

### Log Insights

Use CloudWatch Logs Insights to query logs:

```sql
fields @timestamp, @message
| filter @message like /ERROR/
| sort @timestamp desc
| limit 20
```

## Local Development

### Running Locally

Use the provided batch file (Windows):

```cmd
run-mediscan.bat
```

Or manually:

```bash
# Backend
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py

# Frontend (separate terminal)
cd ..
python -m http.server 5500
```

### Testing Locally

```bash
cd backend
pytest
```

### Linting

```bash
cd backend
flake8 .
```

## Troubleshooting

### Docker Issues

**Container won't start:**
```bash
# Check logs
docker-compose logs backend

# Rebuild
docker-compose up -d --build
```

**Health check failing:**
- Ensure the `/health` endpoint is accessible
- Check port conflicts
- Verify environment variables

### CloudWatch Issues

**Logs not appearing:**
- Verify AWS credentials are correct
- Check IAM permissions (logs:CreateLogGroup, logs:CreateLogStream, logs:PutLogEvents)
- Ensure the log group exists

**Metrics not appearing:**
- Verify CloudWatch permissions (cloudwatch:PutMetricData)
- Check that the application is running with AWS credentials configured

### CI/CD Issues

**Build failing:**
- Check the Actions tab for error details
- Verify secrets are correctly configured
- Ensure Docker Hub credentials are valid

**Deployment failing:**
- Check AWS credentials in GitHub secrets
- Verify deployment target is accessible
- Review deployment logs

## Security Best Practices

1. **Never commit** `.env` files or secrets to Git
2. **Rotate secrets** regularly
3. **Use IAM roles** instead of access keys when possible
4. **Enable MFA** on AWS accounts
5. **Scan images** for vulnerabilities before deployment
6. **Keep dependencies** updated

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [AWS CloudWatch Documentation](https://docs.aws.amazon.com/cloudwatch/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Flask Documentation](https://flask.palletsprojects.com/)

## Support

For issues or questions about the DevOps setup:
1. Check this documentation
2. Review logs in CloudWatch
3. Check GitHub Actions workflow logs
4. Consult the respective tool documentation
