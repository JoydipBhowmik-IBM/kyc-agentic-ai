FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY main.py .

# Create vector DB directory
RUN mkdir -p /data/kyc_vector_db

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV VECTOR_DB_PATH=/data/kyc_vector_db

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8020/health')"

# Expose port
EXPOSE 8020

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8020", "--no-access-log"]
