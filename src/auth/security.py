from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from jose import JWTError, jwt
from pydantic import BaseModel, ValidationError
from typing import Optional

from ..config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

API_KEY_SCHEME_NAME_FOR_SWAGGER = "BearerTokenAuth"
api_key_header_for_swagger = APIKeyHeader(
    name="Authorization",
    description="Insira o token JWT Bearer completo. Formato: \"Bearer SEU_TOKEN_AQUI\"",
    scheme_name=API_KEY_SCHEME_NAME_FOR_SWAGGER,
    auto_error=False
)

class TokenData(BaseModel):
    username: Optional[str] = None

async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais (token inválido ou expirado)",
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
    except JWTError as e:
        print(f"JWTError: {e}")
        raise credentials_exception
    except ValidationError as e:
        print(f"TokenData Pydantic ValidationError: {e}")
        raise credentials_exception

async def ensure_authenticated(token_data: TokenData = Depends(get_current_user)):
    return token_data