# Stage 1: Build stage to install dependencies
FROM python:3.11-slim AS builder

WORKDIR /app

# Create a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium

# Stage 2: Final production stage
FROM python:3.11-slim

# Install system dependencies required for Playwright
RUN apt-get update && apt-get install -y --no-install-recommends \
    libnss3 \
    libnspr4 \
    libdbus-1-3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libglib2.0-0 \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libxtst6 \
    fonts-liberation \
    libappindicator3-1 \
    xdg-utils \
    wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Set path to use the virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# Copy Playwright browser cache from builder stage
COPY --from=builder /root/.cache/ms-playwright /root/.cache/ms-playwright

# Copy application code
COPY ./app /app/app
COPY ./frontend /app/frontend
COPY ./credentials /app/credentials

# Expose port and define command
# The PORT environment variable is set by Render. We default to 8000 for local use.
EXPOSE 8000
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
