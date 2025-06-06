from fastapi import APIRouter, HTTPException, Body, status
from typing import List, Dict, Any
from .schemas import UserLoginRequest, TokenResponse
from . import producao_controller
from . import comercializacao_controller
from . import processamento_controller
from . import importacao_controller
from . import exportacao_controller
from . import auth_controller

router = APIRouter()

router.include_router(auth_controller.router)
router.include_router(producao_controller.router)
router.include_router(comercializacao_controller.router)
router.include_router(processamento_controller.router)
router.include_router(importacao_controller.router)
router.include_router(exportacao_controller.router)

@router.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "message": "API de WebScraping da Embrapa está operacional."}