FROM python:3.11-slim

# System dependencies for OpenCV, glib, libGL
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency specifications first for Docker layer caching
COPY pyproject.toml /app/
COPY threatvision /app/threatvision
COPY README.md /app/

# Install threatvision-ai
RUN pip install --no-cache-dir -e .

EXPOSE 8000

ENV PORT=8000
ENV HOST=0.0.0.0

CMD ["threatvision", "dashboard", "--host", "0.0.0.0", "--port", "8000"]
