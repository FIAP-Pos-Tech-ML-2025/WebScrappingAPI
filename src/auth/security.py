from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.api_key import APIKeyHeader # Mantido
from jose import JWTError, jwt
from pydantic import BaseModel, ValidationError
from typing import Optional

from ..config import settings

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/login"
)

API_KEY_SCHEME_NAME = "BearerAuthAPIKey"
api_key_header_auth_scheme_for_swagger = APIKeyHeader(
    name="Authorization",
    description="Insira o token JWT Bearer completo aqui. Exemplo: \"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...\"",
    scheme_name=API_KEY_SCHEME_NAME,
    auto_error=False
)

class TokenData(BaseModel):
    username: Optional[str] = None

async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        username: Optional[str] = payload.get("sub")
        if username is None:
            username = payload.get("username")
            if username is None:
                raise credentials_exception
        
        token_data = TokenData(username=username)
    except JWTError as e:
        print(f"JWTError: {e}") 
        raise credentials_exception
    except ValidationError as e: 
        print(f"TokenData ValidationError: {e}")
        raise credentials_exception
    
    return token_data

async def ensure_authenticated(token_extracted: str = Depends(oauth2_scheme)):
    await get_current_user(token_extracted)
    return