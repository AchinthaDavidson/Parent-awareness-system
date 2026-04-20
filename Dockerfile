FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create required directories
RUN mkdir -p /app/chroma_db /app/data/pdfs

# Cloud Run sets PORT env var (default 8080)
ENV PORT=8080
EXPOSE 8080

# Start server — reads $PORT so Cloud Run can override it
CMD exec uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1 --timeout-keep-alive 65