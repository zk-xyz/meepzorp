FROM python:3.11-slim

WORKDIR /app

ENV PYTHONPATH=/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN echo '#!/bin/sh\nuvicorn main:app --host 0.0.0.0 --port ${REGISTRY_PORT:-8005}' > /app/start.sh && \
    chmod +x /app/start.sh

EXPOSE ${REGISTRY_PORT:-8005}

CMD ["/app/start.sh"]
