# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/app:/app/agents \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies in smaller chunks with retry logic
RUN pip install --no-cache-dir pip-tools && \
    pip-compile requirements.txt --output-file requirements.lock && \
    pip install --no-cache-dir --retries 3 spacy>=3.7.2 && \
    python -m spacy download en_core_web_sm && \
    pip install --no-cache-dir --retries 3 -r requirements.lock

# Create non-root user
RUN useradd -m -u 1000 agent

# Copy the common agents module
COPY --chown=agent:agent agents/common /app/agents/common
COPY --chown=agent:agent agents/__init__.py /app/agents/

# Copy the personal agent code
COPY --chown=agent:agent agents/personal/src/ /app/src/
COPY --chown=agent:agent agents/personal/__init__.py /app/
COPY --chown=agent:agent agents/personal/setup.py /app/

# Install the package in development mode BEFORE switching user
RUN pip install -e .

# Create startup script
RUN echo '#!/bin/sh\nuvicorn src.main:app --host 0.0.0.0 --port ${AGENT_PORT:-8002}' > /app/start.sh && \
    chmod +x /app/start.sh

# Switch to non-root user
USER agent

# Expose port
EXPOSE ${AGENT_PORT:-8002}

# Start the application
CMD ["/app/start.sh"]