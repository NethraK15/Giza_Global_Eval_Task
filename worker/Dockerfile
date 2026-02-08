FROM python:3.10-slim

WORKDIR /worker

# Install system dependencies for OpenCV and other libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# Install CPU-only PyTorch and other dependencies
RUN pip install --default-timeout=1000 --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu && \
    pip install --default-timeout=1000 --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "worker.py"]
