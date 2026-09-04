# Multi-Stage Dockerfile for QI-Guard Stellar MVP
# Stage 1: Build React Developer Dashboard
FROM node:22-slim AS dashboard-builder
WORKDIR /build
COPY dashboard/package*.json ./
RUN npm install
COPY dashboard/ ./
RUN npm run build

# Stage 2: Python Runtime & FastAPI Application
FROM python:3.12-slim
WORKDIR /app

# Install system utilities and build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY app/ ./app/
COPY API_CONTRACT.md ARCHITECTURE.md DEFINITION_OF_DONE.md ./

# Copy pre-built dashboard distribution from Stage 1
COPY --from=dashboard-builder /build/dist ./dashboard/dist

# Expose API and Dashboard port
EXPOSE 8000

ENV PORT=8000
ENV PYTHONUNBUFFERED=1

# Run FastAPI core service with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
