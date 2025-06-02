from fastapi import APIRouter

from . import producao_controller
from . import comercializacao_controller
from . import processamento_controller
from . import importacao_controller
from . import exportacao_controller

router = APIRouter()

router.include_router(producao_controller.router)
router.include_router(comercializacao_controller.router)
router.include_router(processamento_controller.router)
router.include_router(importacao_controller.router)
router.include_router(exportacao_controller.router)

@router.get("/status", tags=["Status"])
async def status_check():
    return {"status": "ok"}