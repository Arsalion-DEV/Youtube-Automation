FROM nvidia/cuda:11.8-devel-ubuntu22.04

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    git \
    wget \
    curl \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libfontconfig1 \
    libxrender1 \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Install PyTorch with CUDA support
RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install AI model dependencies
RUN pip3 install \
    diffusers==0.21.4 \
    transformers==4.35.2 \
    accelerate==0.24.1 \
    xformers==0.0.22 \
    controlnet-aux==0.0.6 \
    compel==2.0.2 \
    safetensors==0.4.0 \
    invisible-watermark==0.2.0

# Install ComfyUI for AnimateDiff
RUN git clone https://github.com/comfyanonymous/ComfyUI.git /app/ComfyUI
WORKDIR /app/ComfyUI
RUN pip3 install -r requirements.txt

# Install AnimateDiff nodes
RUN git clone https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved.git custom_nodes/ComfyUI-AnimateDiff-Evolved
RUN pip3 install -r custom_nodes/ComfyUI-AnimateDiff-Evolved/requirements.txt

# Install ControlNet nodes
RUN git clone https://github.com/Fannovel16/comfyui_controlnet_aux.git custom_nodes/comfyui_controlnet_aux
RUN pip3 install -r custom_nodes/comfyui_controlnet_aux/requirements.txt

# Back to main app directory
WORKDIR /app

# Install TTS dependencies
RUN pip3 install \
    TTS==0.22.0 \
    bark==1.2.1 \
    piper-tts==1.2.0 \
    tortoise-tts==2.8.0

# Install video processing dependencies
RUN pip3 install \
    moviepy==1.0.3 \
    opencv-python==4.8.1.78 \
    imageio==2.31.5 \
    imageio-ffmpeg==0.4.9

# Install additional dependencies
RUN pip3 install \
    celery==5.3.4 \
    redis==5.0.1 \
    flower==2.0.1 \
    apscheduler==3.10.4 \
    playwright==1.40.0 \
    google-auth==2.23.4 \
    google-auth-oauthlib==1.1.0 \
    google-auth-httplib2==0.1.1 \
    google-api-python-client==2.108.0

# Install Playwright browsers
RUN playwright install chromium

# Create directories
RUN mkdir -p /app/assets/{images,clips,audio} \
    && mkdir -p /app/configs \
    && mkdir -p /app/plugins \
    && mkdir -p /app/models

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -s /bin/bash appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]