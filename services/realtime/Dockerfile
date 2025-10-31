FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY app /app/app

EXPOSE 9000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9000"]

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app .

# Expose port
EXPOSE 8000

# Start the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]