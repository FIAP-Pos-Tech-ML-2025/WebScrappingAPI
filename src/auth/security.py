from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.api_key import APIKeyHeader
from jose import JWTError, jwt
from pydantic import BaseModel, ValidationError
from typing import Optional

from ..config import settings

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/login"
)

api_key_header_auth_scheme = APIKeyHeader(name="Authorization", auto_error=False)

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

async def get_current_user_from_header_for_swagger(
    api_key: Optional[str] = Depends(api_key_header_auth_scheme)
) -> TokenData:
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cabeçalho de autorização ausente",
        )
    
    parts = api_key.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Formato do token inválido. Use: Bearer <token>",
        )
    
    token = parts[1]
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais (via APIKeyHeader)",
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
        
        return TokenData(username=username)
    except JWTError:
        raise credentials_exception
    except ValidationError:
        raise credentials_exception


async def ensure_authenticated(token_extracted: str = Depends(oauth2_scheme)):
    await get_current_user(token_extracted)
    return