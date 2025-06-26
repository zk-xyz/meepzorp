import pytest
from jose import jwt
from fastapi import HTTPException

from agents.common import auth


@pytest.mark.asyncio
async def test_get_current_user_valid():
    token = jwt.encode({"sub": "alice"}, auth.JWT_SECRET, algorithm=auth.ALGORITHM)
    user = await auth.get_current_user(token)
    assert user == "alice"


@pytest.mark.asyncio
async def test_get_current_user_invalid_signature():
    bad_token = jwt.encode({"sub": "alice"}, "wrong", algorithm=auth.ALGORITHM)
    with pytest.raises(HTTPException) as exc:
        await auth.get_current_user(bad_token)
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_missing_token():
    with pytest.raises(HTTPException) as exc:
        await auth.get_current_user("")
    assert exc.value.status_code == 401
