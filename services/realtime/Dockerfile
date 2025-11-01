FROM python:3.12-slim

WORKDIR /app

# Install system dependencies if needed for PyTorch
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt /app/

# Install dependencies and CPU-only PyTorch
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir torch==2.2.2+cpu torchvision==0.17.2+cpu torchaudio==2.2.2+cpu \
        --index-url https://download.pytorch.org/whl/cpu

# Copy application code
COPY app /app/app

EXPOSE 9000

# Start the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9000"]
