FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DJANGO_SETTINGS_MODULE=tictactoe.settings

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        default-libmysqlclient-dev \
        pkg-config \
        curl \
        netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project
COPY . .

# Create entrypoint script
COPY docker-entrypoint.sh /docker-entrypoint.sh
COPY docker-entrypoint-validate.sh /docker-entrypoint-validate.sh
RUN chmod +x /docker-entrypoint.sh /docker-entrypoint-validate.sh

# Create media directory for file persistence
RUN mkdir -p /app/media

# Expose port
EXPOSE 8080

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/health/ || exit 1

# Run entrypoint
ENTRYPOINT ["/docker-entrypoint.sh"]