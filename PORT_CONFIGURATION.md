# Arivu Port Configuration Guide

This guide explains how to configure ports and network settings for the Arivu application across different deployment scenarios.

## Overview

Arivu consists of two main components:
- **Backend**: FastAPI server (default: `127.0.0.1:8000`)
- **Frontend**: Vue.js + Vite dev server (default: `localhost:5173`)

All ports and host addresses are **fully configurable** via environment variables, making it easy to run on different machines with different port availability.

---

## Backend Configuration

### Environment Variables

Configure the backend by setting these variables in [`Arivu/Backend/.env`](Arivu/Backend/.env):

| Variable | Default | Description |
|----------|---------|-------------|
| `ARIVU_BACKEND_HOST` | `127.0.0.1` | Host address to bind the backend server |
| `ARIVU_BACKEND_PORT` | `8000` | Port number for the backend server |
| `ARIVU_CORS_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | Comma-separated list of allowed CORS origins |

### Example `.env` Configuration

```bash
# Server Configuration
ARIVU_BACKEND_HOST=127.0.0.1
ARIVU_BACKEND_PORT=8000
ARIVU_CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

### Running the Backend

**Option 1: Using environment variables (recommended)**
```bash
cd Arivu/Backend
source .venv/bin/activate
python -m uvicorn app.main:app
```

The backend will read `ARIVU_BACKEND_HOST` and `ARIVU_BACKEND_PORT` from the `.env` file.

**Option 2: Using command-line arguments**
```bash
cd Arivu/Backend
source .venv/bin/activate
python -m app.main --host 0.0.0.0 --port 9000
```

Command-line arguments override environment variables.

### CORS Configuration

The `ARIVU_CORS_ORIGINS` setting controls which frontend origins can access the API:

- **Development**: Set to specific origins (e.g., `http://localhost:5173`)
- **Wildcard** (⚠️ security risk): Set to `*` to allow all origins
- **Multiple origins**: Use comma-separated values

```bash
# Allow specific origins (recommended)
ARIVU_CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000

# Allow all origins (development only!)
ARIVU_CORS_ORIGINS=*
```

---

## Frontend Configuration

### Environment Variables

Configure the frontend using `.env.development` or `.env.production` files in [`Arivu/Frontend/vue-project/`](Arivu/Frontend/vue-project/):

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_BASE_URL` | `http://localhost:8000` | Backend API base URL |
| `VITE_BACKEND_URL` | `http://127.0.0.1:8000` | Backend URL for Vite dev proxy |
| `VITE_PORT` | `5173` | Frontend dev server port |

### Example `.env.development`

```bash
# Frontend Development Configuration
VITE_API_BASE_URL=http://localhost:8000
VITE_BACKEND_URL=http://127.0.0.1:8000
```

### Running the Frontend

**Development mode:**
```bash
cd Arivu/Frontend/vue-project
npm run dev
```

**Custom port:**
```bash
npm run dev -- --port 3000
```

**Production build:**
```bash
npm run build
```

---

## Using the Launch Script

The [`start-arivu.command`](start-arivu.command) script starts both backend and frontend automatically.

### Default Behavior

Double-click `start-arivu.command` or run:
```bash
./start-arivu.command
```

This starts:
- Backend on `127.0.0.1:8000`
- Frontend on `localhost:5173`

### Custom Ports via Environment Variables

You can override ports by setting environment variables before running the script:

```bash
export ARIVU_BACKEND_PORT=9000
export ARIVU_BACKEND_HOST=0.0.0.0
export VITE_PORT=3000
./start-arivu.command
```

Or inline:
```bash
ARIVU_BACKEND_PORT=9000 VITE_PORT=3000 ./start-arivu.command
```

---

## Different Deployment Scenarios

### Scenario 1: Default Development Setup
**Use case**: Standard local development

```bash
# Backend .env
ARIVU_BACKEND_HOST=127.0.0.1
ARIVU_BACKEND_PORT=8000
ARIVU_CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# Frontend .env.development
VITE_API_BASE_URL=http://localhost:8000
VITE_BACKEND_URL=http://127.0.0.1:8000
```

Just run: `./start-arivu.command`

---

### Scenario 2: Custom Ports (Port 8000 Already in Use)
**Use case**: Port 8000 is occupied by another service

```bash
# Backend .env
ARIVU_BACKEND_PORT=8080  # Changed from 8000

# Frontend .env.development
VITE_API_BASE_URL=http://localhost:8080  # Must match backend
VITE_BACKEND_URL=http://127.0.0.1:8080   # Must match backend
```

Or use environment variables:
```bash
ARIVU_BACKEND_PORT=8080 ./start-arivu.command
```

**⚠️ Important**: Update `ARIVU_CORS_ORIGINS` to match your frontend port:
```bash
ARIVU_CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

---

### Scenario 3: Network-Accessible Backend
**Use case**: Access backend from other devices on the network

```bash
# Backend .env
ARIVU_BACKEND_HOST=0.0.0.0  # Listen on all interfaces
ARIVU_BACKEND_PORT=8000
ARIVU_CORS_ORIGINS=*  # Allow all origins (development only!)

# Frontend .env.development
VITE_API_BASE_URL=http://192.168.1.100:8000  # Use your machine's IP
```

Find your IP address:
```bash
# macOS/Linux
ifconfig | grep "inet "

# Windows
ipconfig
```

**⚠️ Security Warning**: Using `0.0.0.0` and `CORS_ORIGINS=*` exposes your backend to the entire network. Only use in trusted environments.

---

### Scenario 4: Docker Deployment
**Use case**: Running in Docker containers

#### Backend Dockerfile
```dockerfile
FROM python:3.11

WORKDIR /app
COPY . .
RUN pip install -e .

ENV ARIVU_BACKEND_HOST=0.0.0.0
ENV ARIVU_BACKEND_PORT=8000

CMD ["python", "-m", "app.main"]
```

#### Frontend Dockerfile
```dockerfile
FROM node:20

WORKDIR /app
COPY . .
RUN npm install && npm run build

ENV VITE_API_BASE_URL=http://backend:8000

CMD ["npm", "run", "preview"]
```

#### docker-compose.yml
```yaml
version: '3.8'
services:
  backend:
    build: ./Arivu/Backend
    ports:
      - "8000:8000"
    environment:
      - ARIVU_BACKEND_HOST=0.0.0.0
      - ARIVU_BACKEND_PORT=8000
      - ARIVU_CORS_ORIGINS=http://localhost:5173

  frontend:
    build: ./Arivu/Frontend/vue-project
    ports:
      - "5173:5173"
    environment:
      - VITE_API_BASE_URL=http://backend:8000
    depends_on:
      - backend
```

---

### Scenario 5: Electron App (Production)
**Use case**: Packaged Electron application

In Electron mode, the frontend dynamically discovers the backend URL via IPC:

```typescript
// Frontend: src/main.ts
if ((window as any).electronAPI) {
  const config = await (window as any).electronAPI.getApiConfig()
  setApiBaseUrl(config.baseUrl)  // Dynamically set backend URL
}
```

The Electron main process manages the backend lifecycle and provides the URL.

**Note**: Electron integration is currently a work in progress. The IPC handler needs to be implemented in `electron/main.ts`.

---

## Troubleshooting

### Problem: "Failed to connect to backend"

**Check 1**: Verify backend is running
```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{"status":"ok"}
```

**Check 2**: Verify ports match
- Backend `.env`: `ARIVU_BACKEND_PORT=8000`
- Frontend `.env.development`: `VITE_API_BASE_URL=http://localhost:8000`

**Check 3**: Check CORS configuration
If you see CORS errors in browser console, update `ARIVU_CORS_ORIGINS`:
```bash
ARIVU_CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

---

### Problem: "Port already in use"

**Solution 1**: Find and kill the process using the port
```bash
# macOS/Linux
lsof -ti:8000 | xargs kill -9

# Or change the port
ARIVU_BACKEND_PORT=8080 ./start-arivu.command
```

**Solution 2**: Use a different port
```bash
# Backend .env
ARIVU_BACKEND_PORT=8080

# Frontend .env.development
VITE_API_BASE_URL=http://localhost:8080
VITE_BACKEND_URL=http://127.0.0.1:8080
```

---

### Problem: "Cannot access from other devices"

**Solution**: Bind backend to `0.0.0.0` and use machine's IP address

```bash
# Backend .env
ARIVU_BACKEND_HOST=0.0.0.0
ARIVU_CORS_ORIGINS=*

# On mobile/other device, open:
http://192.168.1.100:5173  # Replace with your machine's IP
```

---

## Configuration Files Reference

### Backend Configuration Files
- [`Arivu/Backend/.env`](Arivu/Backend/.env) - Main backend configuration
- [`Arivu/Backend/app/core/config.py`](Arivu/Backend/app/core/config.py) - Settings schema
- [`Arivu/Backend/app/main.py`](Arivu/Backend/app/main.py) - Entry point with CLI args

### Frontend Configuration Files
- [`Arivu/Frontend/vue-project/.env.development`](Arivu/Frontend/vue-project/.env.development) - Development config
- [`Arivu/Frontend/vue-project/.env.production`](Arivu/Frontend/vue-project/.env.production) - Production config
- [`Arivu/Frontend/vue-project/vite.config.ts`](Arivu/Frontend/vue-project/vite.config.ts) - Vite dev server proxy
- [`Arivu/Frontend/vue-project/src/lib/api.ts`](Arivu/Frontend/vue-project/src/lib/api.ts) - Axios client with base URL

### Launch Scripts
- [`start-arivu.command`](start-arivu.command) - Unified launcher with env var support

---

## Environment Variables Summary

| Variable | Location | Default | Purpose |
|----------|----------|---------|---------|
| `ARIVU_BACKEND_HOST` | Backend `.env` | `127.0.0.1` | Backend bind address |
| `ARIVU_BACKEND_PORT` | Backend `.env` | `8000` | Backend port |
| `ARIVU_CORS_ORIGINS` | Backend `.env` | `http://localhost:5173,...` | Allowed CORS origins |
| `VITE_API_BASE_URL` | Frontend `.env.*` | `http://localhost:8000` | API endpoint for axios |
| `VITE_BACKEND_URL` | Frontend `.env.*` | `http://127.0.0.1:8000` | Vite proxy target |
| `VITE_PORT` | CLI or ENV | `5173` | Frontend dev server port |

---

## Quick Reference Commands

```bash
# Start with default ports
./start-arivu.command

# Start with custom backend port
ARIVU_BACKEND_PORT=9000 ./start-arivu.command

# Start with custom frontend port
VITE_PORT=3000 ./start-arivu.command

# Start with both custom
ARIVU_BACKEND_PORT=9000 VITE_PORT=3000 ./start-arivu.command

# Test backend health
curl http://localhost:8000/api/health

# Check which process is using a port
lsof -i :8000

# Kill process on port
lsof -ti:8000 | xargs kill -9
```

---

## Best Practices

1. **Development**: Use default ports (`8000`, `5173`) for consistency
2. **Environment Variables**: Prefer `.env` files over hardcoded values
3. **CORS Security**: Use specific origins in production, not `*`
4. **Documentation**: Update this file when adding new configuration options
5. **Port Conflicts**: Use `lsof` to detect and resolve port conflicts before starting
6. **Cross-Machine**: Test on different machines to ensure configuration flexibility works

---

## Next Steps / TODO

- [ ] Implement Electron IPC handler for dynamic backend URL configuration
- [ ] Add health check retry logic in frontend for backend startup delays
- [ ] Create systemd/launchd service files for production deployment
- [ ] Add nginx reverse proxy configuration example
- [ ] Document SSL/TLS configuration for HTTPS deployments
- [ ] Add port conflict detection to launch script

---

**Last Updated**: 2026-02-13
**Maintainer**: Arivu Development Team
