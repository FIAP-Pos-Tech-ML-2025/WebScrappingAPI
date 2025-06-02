from fastapi import APIRouter, Depends, HTTPException, Body, status # Adicionado Body, status
from typing import List, Dict, Any
from .schemas import UserLoginRequest, TokenResponse
from ..auth.security import login_via_external_service, ensure_authenticated # Importe ensure_authenticated aqui também se for proteger /health
from . import producao_controller
from . import comercializacao_controller
from . import processamento_controller
from . import importacao_controller
from . import exportacao_controller

router = APIRouter()

@router.post(
    "/auth/loginproxy",
    response_model=TokenResponse,
    tags=["Autenticação"],
    summary="Login do Usuário (via Proxy)",
    description="Autentica um usuário fazendo a chamada para o serviço de autenticação externo e retorna o token de acesso. Use este endpoint na janela 'Authorize' do Swagger UI."
)
async def login_proxy_endpoint(credentials: UserLoginRequest = Body(...)):
    """
    Recebe 'username' e 'password' no corpo da requisição (JSON).
    Chama o serviço de autenticação externo e retorna o token.
    O Swagger UI usará este endpoint quando `tokenUrl` for configurado para ele.
    """
    try:
        token_response = await login_via_external_service(credentials)
        return token_response
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Erro inesperado no endpoint de login proxy: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocorreu um erro interno inesperado durante o login."
        )

router.include_router(producao_controller.router)
router.include_router(comercializacao_controller.router)
router.include_router(processamento_controller.router)
router.include_router(importacao_controller.router)
router.include_router(exportacao_controller.router)

@router.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "message": "API de WebScraping da Embrapa está operacional."}