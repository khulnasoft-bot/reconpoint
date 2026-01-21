# syntax=docker/dockerfile:1
#
# ReconPoint DevContainer Dockerfile
# Production-ready development environment
# Optimized for fast startup, incremental builds, and hot reload
#

# ============================================
# Base Stage: Core dependencies
# ============================================
FROM python:3.10-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies required by Django + packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Build essentials for binary packages (psycopg2, Pillow, etc.)
    build-essential \
    libpq-dev \
    libssl-dev \
    libffi-dev \
    \
    # WeasyPrint/PDF rendering
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    shared-mime-info \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libexif-dev \
    libgobject-2.0-0 \
    libffi-dev \
    gstreamer1.0-plugins-base \
    gstreamer1.0-tools \
    gstreamer1.0-x \
    \
    # Network tools (scapy, nmap)
    libpcap-dev \
    nmap \
    \
    # Git for pre-commit + github operations
    git \
    git-lfs \
    curl \
    wget \
    \
    # Database clients
    postgresql-client \
    \
    # Process management & monitoring
    supervisor \
    htop \
    procps \
    \
    # Utilities
    netcat-openbsd \
    vim \
    nano \
    less \
    ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ============================================
# Development Stage: Dev tools & IDE support
# ============================================
FROM base AS dev

# Create non-root user for development
RUN groupadd -r app && useradd -r -g app app

# Set working directory
WORKDIR /workspaces/reconpoint

# Copy requirements early for layer caching
COPY web/requirements.txt /tmp/requirements.txt

# Install all Python dependencies in a single layer to optimize build cache
RUN pip install --no-cache-dir \
    # Project dependencies first
    -r /tmp/requirements.txt \
    # Core dev tools
    ipython ipdb pdbpp \
    # Testing & coverage
    pytest pytest-django pytest-cov pytest-xdist factory-boy faker \
    # Code quality & formatting (skip duplicates already in requirements.txt)
    flake8-bugbear mypy django-stubs djangorestframework-stubs \
    # Django extensions
    django-debug-toolbar django-extensions django-querycount \
    # Pre-commit
    pre-commit \
    # Performance profiling
    django-silk line-profiler memory-profiler \
    # API documentation & testing
    drf-spectacular \
    # Environment management
    python-dotenv \
    # Security scanning
    bandit safety

# Setup supervisord and git config in single layer
RUN mkdir -p /var/log/supervisor && \
    git config --global --add safe.directory /workspaces/reconpoint

# Copy supervisord config
COPY .devcontainer/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Change ownership to non-root user
RUN chown -R app:app /workspaces

# Switch to non-root user
USER app

# Default command: interactive shell
CMD ["/bin/bash"]
