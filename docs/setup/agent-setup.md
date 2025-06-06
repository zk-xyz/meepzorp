# Agent Setup Guide

This guide details the process of setting up and registering new agents in the Meepzorp Multi-Agent System.

## Agent Registration Process

Agents must register with the orchestration service to participate in the system. Here's how to set up agent registration:

1. **Basic Agent Structure**
   ```
   agents/
   ├── your_agent/
   │   ├── src/
   │   │   ├── main.py         # Main agent code and registration
   │   │   ├── capabilities/   # Agent capabilities
   │   │   └── db.py          # Database operations (if needed)
   │   ├── Dockerfile         # Container configuration
   │   └── setup.py          # Package setup
   ```

2. **Registration Code**
   ```python
   # In src/main.py
   from agents.common.registration import register_agent
   
   @app.on_event("startup")
   async def startup_event():
       """Register agent with orchestration service on startup"""
       capabilities = [
           {
               "name": "your_capability",
               "description": "Description of what this capability does",
               "parameters": {
                   "param1": "type",
                   "param2": "type"
               }
           }
       ]
       
       try:
           await register_agent(
               name="Your Agent Name",
               description="What your agent does",
               capabilities=capabilities
           )
    except Exception as e:
        logger.error(f"Failed to register agent: {str(e)}")
   ```

   The registration request sent to the orchestration service looks like:

   ```json
   {
       "tool": "register_agent",
       "name": "Your Agent Name",
       "description": "What your agent does",
       "endpoint": "http://your-agent:8000",
       "capabilities": [...]
   }
   ```

3. **Docker Configuration**
   ```dockerfile
   # In Dockerfile
   FROM python:3.11-slim
   
   WORKDIR /app
   
   ENV PYTHONPATH=/app:/app/agents
   
   # Copy and install dependencies
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   # Copy agent code
   COPY --chown=agent:agent agents/common /app/agents/common
   COPY --chown=agent:agent agents/your_agent/src/ /app/src/
   
   # Create startup script for proper env var handling
   RUN echo '#!/bin/sh\nuvicorn src.main:app --host 0.0.0.0 --port ${AGENT_PORT:-8000}' > /app/start.sh && \
       chmod +x /app/start.sh
   
   USER agent
   
   EXPOSE ${AGENT_PORT:-8000}
   
   CMD ["/app/start.sh"]
   ```

4. **Docker Compose Entry**
   ```yaml
   your-agent:
     build:
       context: .
       dockerfile: ./agents/your_agent/Dockerfile
     container_name: meepzorp-your-agent
     restart: unless-stopped
     environment:
       - AGENT_PORT=${YOUR_AGENT_PORT:-8000}
       - AGENT_HOST=0.0.0.0
       - AGENT_EXTERNAL_HOST=your-agent:${YOUR_AGENT_PORT:-8000}
       - ORCHESTRATION_URL=http://orchestration:${ORCHESTRATION_PORT:-9810}
     ports:
       - "${YOUR_AGENT_PORT:-8000}:${YOUR_AGENT_PORT:-8000}"
     volumes:
       - ./agents/your_agent/src:/app/src
       - ./agents/common:/app/agents/common
     networks:
       - mcp-net
     depends_on:
       orchestration:
         condition: service_healthy
     healthcheck:
       test: ["CMD", "curl", "-f", "http://localhost:${YOUR_AGENT_PORT:-8000}/health"]
       interval: 10s
       timeout: 5s
       retries: 3
   ```

## Environment Configuration

1. **Required Environment Variables**
   ```
   # In .env
   YOUR_AGENT_PORT=8000              # Choose an available port
   ORCHESTRATION_PORT=9810           # Orchestration service port
   AGENT_HOST=0.0.0.0               # Default host
   ```

2. **Internal vs External Endpoints**
   - Internal (container-to-container): Use container names
     ```
     http://your-agent:8000
     http://orchestration:9810
     ```
   - External (host access): Use localhost/port mapping
     ```
     http://localhost:8000
     http://localhost:9810
     ```

## Health Check Implementation

1. **Basic Health Check Endpoint**
   ```python
   @app.get("/health")
   async def health_check():
       """Health check endpoint"""
       return {"status": "healthy"}
   ```

2. **Advanced Health Check**
   ```python
   @app.get("/health")
   async def health_check():
       """Health check with dependency verification"""
       try:
           # Check database connection
           await db.ping()
           
           # Check orchestration service
           async with httpx.AsyncClient() as client:
               response = await client.get(f"{os.getenv('ORCHESTRATION_URL')}/health")
               response.raise_for_status()
           
           return {
               "status": "healthy",
               "dependencies": {
                   "database": "connected",
                   "orchestration": "connected"
               }
           }
       except Exception as e:
           raise HTTPException(
               status_code=503,
               detail=f"Service unhealthy: {str(e)}"
           )
   ```

## Common Registration Issues

1. **Connection Failures**
   - Check orchestration service is running
   - Verify network connectivity
   - Ensure correct container names and ports

2. **Environment Variables**
   - All required variables are set
   - Values match docker-compose configuration
   - Container names are correct

3. **Port Conflicts**
   - No duplicate port assignments
   - Ports are available on host
   - Port mappings match environment variables

## Best Practices

1. **Agent Development**
   - Start from base agent template
   - Implement health checks
   - Use proper error handling
   - Document capabilities

2. **Registration**
   - Register on startup
   - Handle registration failures gracefully
   - Implement retry logic
   - Log registration status

3. **Configuration**
   - Use environment variables
   - Document required variables
   - Follow port assignment conventions
   - Keep configuration consistent

4. **Testing**
   - Test registration process
   - Verify health checks
   - Check capability execution
   - Test error scenarios 