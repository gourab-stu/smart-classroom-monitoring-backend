FROM python:3.10.16-slim

# Set working directory
WORKDIR /smart-classroom-monitoring-backend

# Copy project files
COPY app/ /smart-classroom-monitoring-backend/
COPY requirements.txt /smart-classroom-monitoring-backend/
COPY .env /smart-classroom-monitoring-backend/

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install dependencies required for common image processing libs (like OpenCV, dlib, face_recognition)
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libopencv-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8000

# Run FastAPI app with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
