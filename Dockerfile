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

# Environment setup - FIXED PATH (moved to end)
ENV PYTHONUNBUFFERED=1
ENV PATH="/home/myuser/.local/bin:${PATH}"

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

CMD python manage.py migrate && \
    python manage.py collectstatic --noinput && \
    gunicorn PyMonitor.wsgi:application --bind 0.0.0.0:$PORT
# CMD python manage.py wait_for_db && \
#     python manage.py migrate && \
#     python manage.py collectstatic --noinput && \
#     gunicorn PyMonitor.wsgi:application --bind 0.0.0.0:$PORT

# # Production command WINDOWS
# CMD python manage.py wait_for_db && \
#     python manage.py migrate && \
#     python manage.py collectstatic --noinput && \
#     waitress-serve --host=0.0.0.0 --port=8000 PyMonitor.wsgi:application

# ==============================================================================
# # Stage 1: Builder - Install all dependencies
# FROM python:3.10-slim as builder

# RUN apt-get update && \
#     apt-get install -y --no-install-recommends \
#     default-libmysqlclient-dev \
#     gcc \
#     pkg-config \
#     && rm -rf /var/lib/apt/lists/*

# WORKDIR /app
# COPY requirements.txt .
# RUN pip install --user --no-cache-dir -r requirements.txt

# # Stage 2: Runtime - Lean production image
# FROM python:3.10-slim
# WORKDIR /app

# # Install system dependencies
# RUN apt-get update && \
#     apt-get install -y --no-install-recommends \
#         curl \
#         default-libmysqlclient-dev \
#         libnss3 libx11-xcb1 libxcomposite1 libxcursor1 libxdamage1 \
#         libxi6 libxtst6 libgtk-3-0 libgbm1 libxss1 libasound2 \
#         fonts-liberation \
#         wget \
#         unzip \
#         xvfb && \
#     apt-get clean && \
#     rm -rf /var/lib/apt/lists/*

# # Install Google Chrome ONLY (no ChromeDriver - webdriver-manager will handle it)
# # RUN wget -q -O /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
# #     apt-get update && \
# #     apt-get install -y --no-install-recommends /tmp/chrome.deb && \
# #     rm /tmp/chrome.deb

# # Create a non-root user
# RUN adduser --disabled-password --gecos "" myuser
# USER myuser

# # Copy installed packages from builder
# COPY --from=builder --chown=myuser:myuser /root/.local /home/myuser/.local

# # Copy application code
# COPY --chown=myuser:myuser . .

# # Environment setup
# ENV PATH=/home/myuser/.local/bin:/usr/local/bin:$PATH
# ENV PYTHONUNBUFFERED=1
# ENV DJANGO_ENV=production
# ENV DISPLAY=:99
# # ENV CHROME_BIN=/usr/bin/google-chrome-stable

# # Health check
# HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
#     CMD curl -f http://localhost:8000/health/ || exit 1

# # Production command with Xvfb for headless browser
# CMD ["sh", "-c", "Xvfb :99 -screen 0 1024x768x16 & export DISPLAY=:99 && python manage.py wait_for_db && python manage.py migrate && python manage.py collectstatic --noinput && waitress-serve --host=0.0.0.0 --port=8000 PyMonitor.wsgi:application"]


