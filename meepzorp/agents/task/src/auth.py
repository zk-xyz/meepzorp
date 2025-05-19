from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[str]:
    """
    Basic authentication dependency that extracts the user ID from the Authorization header.
    In a production environment, this should be replaced with proper JWT validation.
    """
    try:
        # For now, we'll just return the token as the user ID
        # In production, this should validate the JWT and extract the user ID
        return credentials.credentials
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) 