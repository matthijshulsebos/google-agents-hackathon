# Python base
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system deps for pdfplumber and others
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    poppler-utils \
    libxml2 \
    libxslt1.1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# Expose service port for local runs and clarity
EXPOSE 8080

# Uvicorn entry
ENV PORT=8080
CMD ["uvicorn", "app.web:app", "--host", "0.0.0.0", "--port", "8080"]
