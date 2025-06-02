from fastapi import APIRouter, Path, HTTPException
from typing import List, Dict, Any

from ..scraper.core import (
    fetch_embrapa_data,
    get_year_range,
    OPCAO_MAP
)

router = APIRouter(
    prefix="/comercializacao",
    tags=["Comercialização"]
)

OPCAO_COMERCIALIZACAO = OPCAO_MAP["comercializacao"]
SECTION_NAME_COMERCIALIZACAO_PT = "Comercialização"

@router.get("/all",
            summary=f"Obtém todos os dados de {SECTION_NAME_COMERCIALIZACAO_PT} de todos os anos disponíveis",
            description=f"Retorna uma lista de todos os produtos/itens da seção '{SECTION_NAME_COMERCIALIZACAO_PT}' com seus respectivos dados para cada ano disponível no site da Embrapa.",
            response_model=Dict[str, List[Dict[str, Any]]])
async def get_comercializacao_all_years_route():
    try:
        return await fetch_embrapa_data(section_opcao=OPCAO_COMERCIALIZACAO, all_years=True)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Falha ao buscar todos os dados de {SECTION_NAME_COMERCIALIZACAO_PT}: {str(exc)}")

@router.get("/year/{year}",
            summary=f"Obtém dados de {SECTION_NAME_COMERCIALIZACAO_PT} para um ano específico",
            description=f"Retorna os dados de {SECTION_NAME_COMERCIALIZACAO_PT} para o ano especificado. O ano deve estar dentro do intervalo disponível no site da Embrapa.",
            response_model=Dict[str, List[Dict[str, Any]]])
async def get_comercializacao_by_year_route(
    year: int = Path(..., title="Ano", description="O ano para o qual buscar os dados")
):
    try:
        min_year, max_year = await get_year_range(section_opcao=OPCAO_COMERCIALIZACAO)
        if min_year is None or max_year is None:
            raise HTTPException(status_code=404, detail=f"Não foi possível determinar o intervalo de anos para {SECTION_NAME_COMERCIALIZACAO_PT}.")
        if not (min_year <= year <= max_year):
            raise HTTPException(
                status_code=400,
                detail=f"Ano {year} fora do intervalo para {SECTION_NAME_COMERCIALIZACAO_PT}. Intervalo disponível: [{min_year}-{max_year}]"
            )
        return await fetch_embrapa_data(section_opcao=OPCAO_COMERCIALIZACAO, year_to_fetch=year)
    except HTTPException as http_exc:
        raise http_exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Falha ao buscar dados de {SECTION_NAME_COMERCIALIZACAO_PT} para o ano {year}: {str(exc)}")

@router.get("",
            summary=f"Obtém dados de {SECTION_NAME_COMERCIALIZACAO_PT} do último ano disponível",
            description=f"Retorna os dados de {SECTION_NAME_COMERCIALIZACAO_PT} referentes ao ano mais recente com dados disponíveis no site da Embrapa.",
            response_model=Dict[str, List[Dict[str, Any]]])
async def get_comercializacao_latest_year_route():
    try:
        _, max_year = await get_year_range(section_opcao=OPCAO_COMERCIALIZACAO)
        if max_year is None:
            raise HTTPException(status_code=404, detail=f"Não foi possível determinar o último ano para {SECTION_NAME_COMERCIALIZACAO_PT}.")
        return await fetch_embrapa_data(section_opcao=OPCAO_COMERCIALIZACAO, year_to_fetch=max_year)
    except HTTPException as http_exc:
        raise http_exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Falha ao buscar os dados mais recentes de {SECTION_NAME_COMERCIALIZACAO_PT}: {str(exc)}")