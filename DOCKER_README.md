# Docker Setup Instructions

## Quick Start

1. **Clone or navigate to the project directory:**
   ```bash
   cd TicTacToeRecurcive-main
   ```

2. **Build and run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

3. **Access the application:**
   - Open your browser and go to: `http://localhost:8000`
   - Admin panel: `http://localhost:8000/admin/`
   - Default admin credentials: `admin` / `admin123`

## Services

The Docker setup includes:

- **web**: Django application with Daphne ASGI server
- **db**: MySQL 8.0 database
- **redis**: Redis for Django Channels WebSocket support

## Environment Variables

Copy `.env.example` to `.env` and modify as needed:

```bash
cp .env.example .env
```

## Development

For development with auto-reload:

```bash
# Stop the containers
docker-compose down

docker-compose up --build
```

## Database

The MySQL database is persistent. To reset:

```bash
docker-compose down -v  # This removes volumes
docker-compose up --build
```

## Logs

View logs for all services:
```bash
docker-compose logs -f
```

View logs for a specific service:
```bash
docker-compose logs -f web
```

## Troubleshooting

1. **Port conflicts**: If port 8000, 3306, or 6379 are in use, modify `docker-compose.yml`
2. **Permission issues**: Ensure `docker-entrypoint.sh` is executable
3. **Database connection errors**: Wait for MySQL to fully start (health check included)
