# Build stage
FROM python:3.9-slim as builder

WORKDIR /app

# Install only essential build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.9-slim

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy only essential application files
COPY ./app ./app

# Create required directories (even if empty)
RUN mkdir -p alembic migrations

# Environment variables
ENV PYTHONPATH=/app \
    PORT=8000

EXPOSE $PORT

CMD ["sh", "-c", "gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT"]
