FROM python:3.10-slim

# Install system dependencies for Tesseract and image format support
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    imagemagick \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
