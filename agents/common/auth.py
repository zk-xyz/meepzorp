"""
Authentication module for MCP agents.

This module provides authentication utilities for FastAPI agents using
JWT-based Bearer tokens. Tokens are validated and decoded to determine
the current user.
"""

from typing import Annotated

import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

# Initialize OAuth2 scheme with token URL
# Note: This URL is just a placeholder - tokens are not actually issued here
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# JWT configuration
JWT_SECRET = os.getenv("JWT_SECRET", "secret")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> str:
    """
    Dependency that extracts and validates the current user from the OAuth2 token.
    
    Decodes and verifies a JWT token to extract the user ID.  The token is
    expected to contain a ``sub`` claim identifying the user.  Tokens are
    validated using the ``JWT_SECRET`` and ``ALGORITHM`` defined above.
    
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

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        user_id: str | None = payload.get("sub") or payload.get("user_id")
        if not user_id:
            raise JWTError("Missing subject")
        return user_id
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
