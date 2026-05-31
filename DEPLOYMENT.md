# MediScan Deployment Guide

This guide provides step-by-step instructions for deploying MediScan using Docker and Vercel.

## Prerequisites

- Docker and Docker Compose installed
- Git
- Vercel account (for frontend deployment)
- Backend hosting service (Render, Railway, AWS, etc.) for production

---

## Option 1: Full Docker Deployment (Recommended for Development/Testing)

### Step 1: Prepare Environment Variables

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and set your production values:
   - `JWT_SECRET_KEY`: Generate a secure random key
   - `ALLOWED_ORIGINS`: Set to your frontend domain (e.g., `https://your-frontend.vercel.app`)

### Step 2: Build and Run with Docker Compose

1. Build the Docker images:
```bash
docker-compose build
```

2. Start the services:
```bash
docker-compose up -d
```

3. Verify the services are running:
```bash
docker-compose ps
```

4. Check logs if needed:
```bash
docker-compose logs -f
```

### Step 3: Access the Application

- Frontend: http://localhost
- Backend API: http://localhost:8000
- Health check: http://localhost:8000/health

### Step 4: Docker Management Commands

- Stop services: `docker-compose down`
- Stop and remove volumes: `docker-compose down -v`
- Rebuild after changes: `docker-compose up -d --build`
- View backend logs: `docker-compose logs backend`

---

## Option 2: Vercel Frontend + Cloud Backend (Recommended for Production)

### Step 1: Deploy Backend to Cloud Service

Choose a cloud hosting service for your backend (Render, Railway, AWS, etc.):

#### Example: Deploy to Render

1. Push your code to GitHub
2. Create a new Web Service on Render
3. Connect your GitHub repository
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `python main.py`
6. Add environment variables:
   - `FLASK_ENV=production`
   - `FLASK_RUN_HOST=0.0.0.0`
   - `FLASK_RUN_PORT=8000`
   - `JWT_SECRET_KEY=your-secure-key`
   - `ALLOWED_ORIGINS=https://your-frontend.vercel.app`
7. Deploy

#### Example: Deploy to Railway

1. Install Railway CLI: `npm install -g @railway/cli`
2. Login: `railway login`
3. Initialize: `railway init`
4. Add backend service: `railway add backend`
5. Set environment variables in Railway dashboard
6. Deploy: `railway up`

### Step 2: Update Frontend API Configuration

1. Edit `frontend/api-config.js`
2. Replace the production URL with your deployed backend URL:
```javascript
return 'https://your-backend-url.onrender.com'; // or your actual backend URL
```

### Step 3: Deploy Frontend to Vercel

#### Option A: Using Vercel CLI

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Navigate to frontend directory:
```bash
cd frontend
```

3. Deploy:
```bash
vercel
```

4. Follow the prompts:
   - Set project name
   - Link to existing project (if any)
   - Confirm settings

5. Deploy to production:
```bash
vercel --prod
```

#### Option B: Using Vercel Dashboard

1. Go to [vercel.com](https://vercel.com) and sign in
2. Click "Add New Project"
3. Import your Git repository
4. Configure:
   - **Framework Preset**: Other
   - **Root Directory**: `frontend`
   - **Build Command**: (leave empty for static site)
   - **Output Directory**: `./`
5. Add environment variables (if needed)
6. Click "Deploy"

### Step 4: Verify Deployment

1. Visit your Vercel URL
2. Test the application functionality
3. Check browser console for API connection errors
4. Verify API calls are reaching your backend

---

## File Organization

### Project Structure

```
mediscan/
├── backend/
│   ├── Dockerfile              # Docker image for backend
│   ├── .dockerignore           # Files to exclude from Docker build
│   ├── .env.example            # Environment variables template
│   ├── main.py                 # Flask application entry point
│   ├── requirements.txt        # Python dependencies
│   ├── data/                   # SQLite database and data files
│   └── models/                 # Pre-trained ML models
├── frontend/
│   ├── Dockerfile              # Docker image for frontend (nginx)
│   ├── .dockerignore           # Files to exclude from Docker build
│   ├── .gitignore              # Files to exclude from Git
│   ├── vercel.json             # Vercel deployment configuration
│   ├── nginx.conf              # Nginx configuration for Docker
│   ├── api-config.js           # API endpoint configuration
│   ├── index.html              # Main landing page
│   ├── login.html              # Login page
│   ├── register.html           # Registration page
│   ├── dashboard.html          # User dashboard
│   └── mediscan-ai.html        # Main AI interface
├── docker-compose.yml          # Docker Compose configuration
├── .env.example                # Environment variables template
└── DEPLOYMENT.md               # This file
```

### Files to Ignore (Already Configured)

The following files are excluded from Docker builds via `.dockerignore`:
- `.venv/`, `env/` - Virtual environments
- `__pycache__/`, `*.pyc` - Python cache
- `*.log` - Log files
- `*.bat`, `*.ps1` - Windows scripts
- `bat_err.txt`, `bat_out.txt` - Temporary files
- Test files and development scripts

---

## Troubleshooting

### Docker Issues

**Problem: Containers won't start**
- Check logs: `docker-compose logs`
- Verify ports aren't in use: `netstat -ano | findstr :80` and `:8000`
- Rebuild images: `docker-compose build --no-cache`

**Problem: Backend can't connect to database**
- Check volume is mounted: `docker-compose inspect backend`
- Verify data directory permissions
- Check database path in environment variables

### Vercel Issues

**Problem: Frontend can't reach backend**
- Verify backend URL in `api-config.js`
- Check CORS settings in backend (`ALLOWED_ORIGINS`)
- Ensure backend is deployed and accessible
- Check browser console for CORS errors

**Problem: Build fails on Vercel**
- Verify `vercel.json` configuration
- Check that all required files are in the frontend directory
- Ensure no build command is needed for static HTML

---

## Security Best Practices

1. **Never commit `.env` files** - Use `.env.example` as template
2. **Change JWT_SECRET_KEY** in production - Use a strong random key
3. **Set ALLOWED_ORIGINS** - Restrict to your actual frontend domain
4. **Use HTTPS** - Ensure both frontend and backend use HTTPS in production
5. **Keep dependencies updated** - Regularly update Python and npm packages
6. **Monitor logs** - Set up logging and monitoring for production

---

## Environment Variables Reference

### Backend Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `FLASK_ENV` | Flask environment | `production` | No |
| `FLASK_RUN_HOST` | Host to bind to | `0.0.0.0` | No |
| `FLASK_RUN_PORT` | Port to bind to | `8000` | No |
| `JWT_SECRET_KEY` | Secret key for JWT tokens | `mediscan-change-in-production` | Yes |
| `ALLOWED_ORIGINS` | CORS allowed origins | `*` | Yes |
| `DATABASE_URL` | SQLite database path | `sqlite:////app/data/mediscan.db` | No |
| `AWS_ACCESS_KEY_ID` | AWS access key (optional) | - | No |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key (optional) | - | No |
| `AWS_REGION` | AWS region | `us-east-1` | No |

---

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Docker logs: `docker-compose logs`
3. Check browser console for frontend errors
4. Verify backend health: `curl http://your-backend/health`
