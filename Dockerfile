# Use a multi-stage build for production
FROM python:3.10-slim as builder

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    gcc \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.10-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        default-libmysqlclient-dev \
        && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN adduser --disabled-password --gecos "" myuser
USER myuser

# Copy installed packages from builder - FIXED PATH
COPY --from=builder --chown=myuser:myuser /root/.local /home/myuser/.local

# Copy application code
COPY --chown=myuser:myuser . .

# Environment setup
ENV PYTHONUNBUFFERED=1
ENV PATH="/home/myuser/.local/bin:${PATH}"

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

CMD python manage.py migrate && \
    python manage.py collectstatic --noinput && \
    gunicorn PyMonitor.wsgi:application --bind 0.0.0.0:$PORT
