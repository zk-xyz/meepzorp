FROM python:3.11-slim

WORKDIR /app

# Set Python path to include /app, /app/src, and /app/common
ENV PYTHONPATH=/app:/app/src:/app/common

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m agent

# Copy application code
COPY --chown=agent:agent . .

# Copy common directory from agents/common
COPY --chown=agent:agent agents/common /app/common

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Switch to non-root user
USER agent

# Expose port
EXPOSE 8003

# Start the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8003"] 