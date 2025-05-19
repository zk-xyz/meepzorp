"""
Authentication module for MCP agents.

This module provides common authentication functionality using FastAPI's OAuth2 scheme.
Currently implements a simplified version that uses the token as the user ID.
Future improvements could include JWT validation, role-based access, etc.
"""

from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# Initialize OAuth2 scheme with token URL
# Note: This URL is just a placeholder - tokens are not actually issued here
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> str:
    """
    Dependency that extracts and validates the current user from the OAuth2 token.
    
    Currently implements a simplified version that returns the token as the user ID.
    Future improvements could include proper JWT validation, user lookup, etc.
    
    Args:
        token: The OAuth2 token from the request
        
    Returns:
        str: The user ID (currently just the token value)
        
    Raises:
        HTTPException: If the token is invalid or expired
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # TODO: Add proper token validation and user lookup
    # For now, just return the token as the user ID
    return token 