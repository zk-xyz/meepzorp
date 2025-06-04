# Port Configuration Guide

This guide details the port configuration setup for the Meepzorp Multi-Agent System.

## Service Ports

The following ports are used by various services in the system:

| Service | Port | Description |
|---------|------|-------------|
| Orchestration | 9810 | Main orchestration service for agent registration and tool routing |
| Base Agent | 8001 | Template for new agent development |
| Personal Agent | 8002 | Personal knowledge agent |
| Task Agent | 8003 | Task management agent |
| UI | 3000 | Management dashboard |
| Redis | 6379 | Cache and pub/sub messaging |

## Port Configuration Process

When setting up a new project or agent, follow these steps to ensure correct port configuration:

1. **Environment Variables**
   - Copy `.env.example` to `.env`
   - Set the following port variables:
     ```
    ORCHESTRATION_PORT=9810
    BASE_AGENT_PORT=8001
    PERSONAL_AGENT_PORT=8002
    TASK_AGENT_PORT=8003
    REDIS_PORT=6379
    UI_PORT=3000
    ```

2. **Docker Compose Configuration**
   - Ensure port mappings in `docker-compose.yml` match the environment variables
   - Use the format: `"${SERVICE_PORT:-default}:${SERVICE_PORT:-default}"`
   - Example:
     ```yaml
     ports:
       - "${ORCHESTRATION_PORT:-9810}:${ORCHESTRATION_PORT:-9810}"
     ```

3. **Agent Dockerfile Setup**
   - Create a startup script to handle environment variable substitution:
     ```dockerfile
     RUN echo '#!/bin/sh\nuvicorn src.main:app --host 0.0.0.0 --port ${AGENT_PORT:-8000}' > /app/start.sh && \
         chmod +x /app/start.sh
     
     EXPOSE ${AGENT_PORT:-8000}
     
     CMD ["/app/start.sh"]
     ```

4. **Agent Registration Configuration**
   - Set `AGENT_HOST` and `AGENT_PORT` in environment
   - Use container names for internal communication
   - Example environment variables:
     ```
     AGENT_HOST=0.0.0.0
     AGENT_PORT=8002
     AGENT_EXTERNAL_HOST=personal-agent:8002
     ORCHESTRATION_URL=http://orchestration:9810
     ```

## Docker Networking

The system uses Docker's internal networking for service communication:

1. **Internal Communication**
   - Services communicate using container names (e.g., `http://orchestration:9810`)
   - Container names are automatically resolved within the Docker network

2. **External Access**
   - Services are exposed to the host machine through port mappings
   - Use `localhost` or `127.0.0.1` to access services from the host

3. **Health Checks**
   - Configure health checks using internal ports
   - Example:
     ```yaml
     healthcheck:
       test: ["CMD", "curl", "-f", "http://localhost:${AGENT_PORT:-8002}/health"]
     ```

## Common Issues and Solutions

1. **Port Already in Use**
   - Check for conflicting services on the host machine
   - Update port numbers in `.env` if needed
   - Restart Docker services after port changes

2. **Registration Failures**
   - Verify orchestration service is healthy
   - Check container name resolution
   - Ensure ports match between registration and service configuration

3. **Environment Variable Substitution**
   - Use shell script for uvicorn startup to handle variable substitution
   - Verify environment variables are properly passed to containers
   - Check for default values in Dockerfile and docker-compose.yml

## Best Practices

1. **Port Standardization**
   - Keep port assignments consistent across environments
   - Document any deviations from standard ports
   - Use port ranges for similar services (e.g., 8001-8009 for agents)

2. **Configuration Management**
   - Keep port configurations in `.env` file
   - Use environment variables in Docker configurations
   - Document port assignments in README.md

3. **Health Monitoring**
   - Implement health check endpoints for all services
   - Configure Docker health checks
   - Monitor port availability and service connectivity

4. **Security Considerations**
   - Expose only necessary ports
   - Use internal Docker networking when possible
   - Configure proper access controls for exposed ports 