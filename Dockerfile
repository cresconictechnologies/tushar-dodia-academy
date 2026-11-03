# Production Dockerfile for Tushar Dodia Executive Mentorship & Dodia Academy
FROM mcr.microsoft.com/playwright/python:v1.48.0-jammy

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PORT=8000 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Ensure Playwright Chromium browser is installed
RUN playwright install chromium

# Copy application source code
COPY . .

# Create persistent download and data directories if they don't exist
RUN mkdir -p dossier/downloads dossier/pages

# Expose target port
EXPOSE 8000

# Run uvicorn on container startup
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}"]
