# TicTacToe Docker Deployment

This document provThe application will be available at http://localhost:8080

## Architecture

The application consists of:

- **Django Web Application**: Runs on port 8080 internally, served by Daphne ASGI server
- **WhiteNoise Middleware**: Efficiently serves static and media files  
- **MySQL Database**: Persistent data storage  
- **Redis**: Cache and WebSocket support for Django Channels

## Services

- **Web Application**: `http://localhost:8080` (main access point)
- **Web Application Alternative**: `http://localhost:8000` (alternative access)
- **MySQL Database**: `localhost:3307` (external access)
- **Redis**: `localhost:6380` (external access) for deploying the TicTacToe application using Docker.

## Requirements

- Docker
- Docker Compose

## Quick Start

1. Clone the repository:
```bash
git clone <repository-url>
cd TicTacToeRecurcive-main
```

2. Start the application:
```bash
docker compose up -d
```

The application will be available at http://localhost:8081

## Docker Compose Files

The project includes three docker-compose configurations:

### 1. **docker-compose.yml** (Default - Development/Testing)
```bash
docker compose up -d
```
- Exposes both port 8000 and 8081
- Debug mode enabled
- Good for development and testing

### 2. **docker-compose.prod.yml** (Production)
```bash
docker compose -f docker-compose.prod.yml up -d
```
- Production optimized settings
- Debug mode disabled (`DEBUG=false`)
- Same functionality with production security settings

### 3. **docker-compose.validate.yml** (Validation/Testing)
```bash
docker compose -f docker-compose.validate.yml up -d
```
- Enhanced validation and testing
- Uses validation entrypoint script
- Extended health check periods
- Best for deployment validation

## Architecture

The application consists of:

- **Django Web Application**: Runs on port 8080 internally, served by Daphne ASGI server
- **WhiteNoise Middleware**: Efficiently serves static and media files  
- **MySQL Database**: Persistent data storage  
- **Redis**: Cache and WebSocket support for Django Channels

## Services

- **Web Application**: `http://localhost:8081` (main access point)
- **Web Application Alternative**: `http://localhost:8000` (alternative access)
- **MySQL Database**: `localhost:3307` (external access)
- **Redis**: `localhost:6380` (external access)

## Health Checks

The application includes health check endpoints:
- `/health/` - Main health check endpoint
- `/healthz/` - Alternative health check endpoint

## File Persistence

- **Static files**: Served by Nginx from persistent volume
- **Media files**: Persistent volume mounted at `/app/media`
- **Database**: MySQL data stored in persistent volume

## Production Deployment

For production, use the production compose file:

```bash
docker compose -f docker-compose.prod.yml up -d
```

For validation and testing:

```bash
docker compose -f docker-compose.validate.yml up -d
```

This configuration:
- Sets `DEBUG=false`
- Uses production-optimized settings
- Includes all security headers via WhiteNoise
- Enhanced validation with deployment checks

## Features

✅ **Port 8080**: Application accessible on port 8080 (also available on 8000)  
✅ **Two-command deployment**: `git clone` + `docker compose up -d`  
✅ **No runserver**: Uses Daphne ASGI server for production  
✅ **MySQL Database**: Production-ready database (not SQLite)  
✅ **Static/Media Files**: Efficiently served by WhiteNoise middleware  
✅ **Automatic Migrations**: Applied automatically on startup  
✅ **Health Checks**: Available at `/health/` and `/healthz/`  
✅ **Media Persistence**: Files persist across container restarts  
✅ **WebSocket Support**: Real-time features with Django Channels  
✅ **No System Check Errors**: Django runs cleanly in production mode  

## Default Admin User

A default superuser is created automatically:
- **Username**: admin
- **Password**: admin123
- **Email**: admin@example.com

## Logs

View application logs:
```bash
docker compose logs -f web
docker compose logs -f nginx
docker compose logs -f db
```

## Cleanup

Stop and remove all containers and volumes:
```bash
docker compose down -v
```

Stop containers but keep data:
```bash
docker compose down
```
