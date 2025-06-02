from fastapi import APIRouter, Path, HTTPException, Depends
from typing import List, Dict, Any

from ..scraper.core import (
    fetch_embrapa_data,
    get_year_range,
    OPCAO_MAP
)
from ..auth.security import ensure_authenticated

router = APIRouter(
    prefix="/producao",
    tags=["Produção"],
    dependencies=[Depends(ensure_authenticated)]
)

OPCAO_PRODUCAO = OPCAO_MAP["producao"]
SECTION_NAME_PRODUCAO_PT = "Produção"

@router.get("/all",
            summary=f"Obtém todos os dados de {SECTION_NAME_PRODUCAO_PT} de todos os anos disponíveis",
            description=f"Retorna uma lista de todos os produtos/itens da seção '{SECTION_NAME_PRODUCAO_PT}' com seus respectivos dados para cada ano disponível no site da Embrapa.",
            response_model=Dict[str, List[Dict[str, Any]]])
async def get_producao_all_years_route():
    try:
        return await fetch_embrapa_data(section_opcao=OPCAO_PRODUCAO, all_years=True)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Falha ao buscar todos os dados de {SECTION_NAME_PRODUCAO_PT}: {str(exc)}")

@router.get("/year/{year}",
            summary=f"Obtém dados de {SECTION_NAME_PRODUCAO_PT} para um ano específico",
            description=f"Retorna os dados de {SECTION_NAME_PRODUCAO_PT} para o ano especificado. O ano deve estar dentro do intervalo disponível no site da Embrapa.",
            response_model=Dict[str, List[Dict[str, Any]]])
async def get_producao_by_year_route(
    year: int = Path(..., title="Ano", description="O ano para o qual buscar os dados (ex: 2020)")
):
    try:
        min_year, max_year = await get_year_range(section_opcao=OPCAO_PRODUCAO)
        if min_year is None or max_year is None:
            raise HTTPException(status_code=404, detail=f"Não foi possível determinar o intervalo de anos para {SECTION_NAME_PRODUCAO_PT}.")
        if not (min_year <= year <= max_year):
            raise HTTPException(
                status_code=400,
                detail=f"Ano {year} fora do intervalo para {SECTION_NAME_PRODUCAO_PT}. Intervalo disponível: [{min_year}-{max_year}]"
            )
        return await fetch_embrapa_data(section_opcao=OPCAO_PRODUCAO, year_to_fetch=year)
    except HTTPException as http_exc:
        raise http_exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Falha ao buscar dados de {SECTION_NAME_PRODUCAO_PT} para o ano {year}: {str(exc)}")

@router.get("",
            summary=f"Obtém dados de {SECTION_NAME_PRODUCAO_PT} do último ano disponível",
            description=f"Retorna os dados de {SECTION_NAME_PRODUCAO_PT} referentes ao ano mais recente com dados disponíveis no site da Embrapa.",
            response_model=Dict[str, List[Dict[str, Any]]])
async def get_producao_latest_year_route():
    try:
        _, max_year = await get_year_range(section_opcao=OPCAO_PRODUCAO)
        if max_year is None:
            raise HTTPException(status_code=404, detail=f"Não foi possível determinar o último ano para {SECTION_NAME_PRODUCAO_PT}.")
        return await fetch_embrapa_data(section_opcao=OPCAO_PRODUCAO, year_to_fetch=max_year)
    except HTTPException as http_exc:
        raise http_exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Falha ao buscar os dados mais recentes de {SECTION_NAME_PRODUCAO_PT}: {str(exc)}")