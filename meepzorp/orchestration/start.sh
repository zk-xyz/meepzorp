#!/bin/bash
exec uvicorn main:app --host 0.0.0.0 --port ${MCP_PORT:-9810} 