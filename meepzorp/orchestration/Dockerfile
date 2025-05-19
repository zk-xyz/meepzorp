FROM python:3.11-slim

WORKDIR /app

ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m agent

# Copy application files (from orchestration context)
COPY --chown=agent:agent . .

# Install Python dependencies from the copied location
RUN pip install --no-cache-dir -r /app/requirements.txt

# Set up start script permissions (copied to /app/start.sh)
RUN chmod +x /app/start.sh

# Switch to non-root user
USER agent

# Expose port
EXPOSE ${MCP_PORT:-9810}

# Start the application using the correct path
# The start.sh script already cds into /app/src
CMD ["/app/start.sh"] 