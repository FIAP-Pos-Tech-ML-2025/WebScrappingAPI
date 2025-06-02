import httpx
from typing import Optional
from ..config import settings
from jose import JWTError, jwt
from pydantic import BaseModel, ValidationError
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from ..api.schemas import TokenResponse as APITokenResponse
from ..api.schemas import UserLoginRequest as APIUserLoginRequest

PROXY_LOGIN_ENDPOINT_FULL_PATH = "/api/v1/auth/loginproxy" 

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=PROXY_LOGIN_ENDPOINT_FULL_PATH
)

class TokenData(BaseModel):
    username: Optional[str] = None


async def login_via_external_service(login_credentials: APIUserLoginRequest) -> APITokenResponse:
    external_auth_url = f"{settings.AUTH_SERVICE_URL.rstrip('/')}/auth/login"
    
    async with httpx.AsyncClient() as client:
        try:
            print(f"Proxying login for '{login_credentials.username}' to '{external_auth_url}'")
            response = await client.post(external_auth_url, json=login_credentials.model_dump())
            
            response.raise_for_status()
            
            token_json = response.json()
            return APITokenResponse(**token_json)
            
        except httpx.HTTPStatusError as exc:
            error_detail_msg = "Credenciais inválidas ou erro no serviço de autenticação externo."
            if exc.response and exc.response.content:
                try:
                    error_content = exc.response.json()
                    if isinstance(error_content, dict) and "detail" in error_content:
                        error_detail_msg = str(error_content["detail"])
                except Exception:
                    pass 
            print(f"Error from external auth service: {exc.response.status_code} - {error_detail_msg if exc.response else 'No response content'}")
            raise HTTPException(
                status_code=exc.response.status_code if exc.response else status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=error_detail_msg,
            )
        except httpx.RequestError as exc:
            print(f"RequestError calling external auth service at {exc.request.url}: {exc}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Erro de comunicação com o serviço de autenticação.",
            )
        except Exception as e:
            print(f"Unexpected error in login_via_external_service: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao processar a autenticação.",
            )

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
        print(f"JWTError decoding token: {e}") 
        raise credentials_exception
    except ValidationError as e:
        print(f"TokenData Pydantic ValidationError: {e}")
        raise credentials_exception
    
    return token_data

async def ensure_authenticated(token_extracted: str = Depends(oauth2_scheme)):
    await get_current_user(token_extracted)
    return