# PentestAgent - AI Penetration Testing Agent
# Base image with common tools

FROM python:3.14-slim

LABEL maintainer="PentestAgent"
LABEL description="AI penetration testing"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV TOKENIZERS_PARALLELISM=false

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Basic utilities
    curl \
    wget \
    git \
    vim \
    # Network tools
    nmap \
    netcat-openbsd \
    dnsutils \
    iputils-ping \
    traceroute \
    tcpdump \
    # Web tools
    httpie \
    # VPN support
    openvpn \
    wireguard-tools \
    # Build tools
    build-essential \
    libffi-dev \
    libssl-dev \
    xclip \
    # Clean up
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Install Python dependencies
COPY pyproject.toml README.md ./
RUN mkdir -p pentestagent && touch pentestagent/__init__.py && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e ".[rag]"

# Create non-root user for security
RUN useradd -m -s /bin/bash pentestagent && \
    chown -R pentestagent:pentestagent /app

RUN playwright install-deps

# Switch to non-root user (can switch back for privileged operations)
USER pentestagent

RUN playwright install

# Copy application code
COPY --chown=pentestagent:pentestagent . .

# Expose any needed ports
EXPOSE 8080

# Default command
CMD ["python", "-m", "pentestagent"]
