from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
import httpx
from typing import Dict

from ..config import settings
from .schemas import TokenResponse

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/login", response_model=TokenResponse)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Logs in a user by forwarding credentials to the external authentication service
    and returns a JWT access token.
    """
    auth_service_login_url = f"{settings.AUTH_SERVICE_URL.rstrip('/')}/login"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                auth_service_login_url,
                data={"username": form_data.username, "password": form_data.password}
            )

            if response.status_code == status.HTTP_200_OK:
                token_data = response.json()
                return TokenResponse(access_token=token_data.get("access_token"), token_type=token_data.get("token_type", "bearer"))
            elif response.status_code == status.HTTP_400_BAD_REQUEST or \
                 response.status_code == status.HTTP_401_UNAUTHORIZED:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                print(f"Error from auth service: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Authentication service unavailable or returned an error.",
                )
    except httpx.RequestError as exc:
        print(f"RequestError connecting to auth service: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Could not connect to authentication service: {str(exc)}",
        )
    except Exception as e:
        print(f"Unexpected error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during login.",
        )