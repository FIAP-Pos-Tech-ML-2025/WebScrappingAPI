from fastapi import APIRouter, Path, HTTPException
from typing import List, Dict, Any

from ..scraper.core import (
    fetch_embrapa_data,
    get_year_range,
    get_available_suboptions,
    OPCAO_MAP
)

router = APIRouter(
    prefix="/importacao",
    tags=["Importação"]
)

SECTION_NAME_PT = "Importação"
CURRENT_SECTION_OPCAO = OPCAO_MAP["importacao"]

@router.get("/suboptions",
            summary=f"Lista as subopções disponíveis para {SECTION_NAME_PT}",
            description=f"Retorna uma lista de nomes e valores das subopções (categorias de importação, como 'Vinhos de mesa') disponíveis na seção de {SECTION_NAME_PT} do site da Embrapa.",
            response_model=List[Dict[str, str]])
async def list_suboptions_route():
    try:
        return await get_available_suboptions(section_opcao=CURRENT_SECTION_OPCAO)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Falha ao listar subopções para {SECTION_NAME_PT}: {str(exc)}")

@router.get("/{subopcao_value}/all",
            summary=f"Obtém todos os dados de uma subopção de {SECTION_NAME_PT} de todos os anos",
            description=f"Retorna dados agregados para uma subopção específica de {SECTION_NAME_PT} (ex: 'Vinhos de mesa'), abrangendo todos os anos disponíveis no site da Embrapa.",
            response_model=Dict[str, List[Dict[str, Any]]])
async def get_suboption_all_years_route(
    subopcao_value: str = Path(..., title="Valor da Subopção", description="O valor da subopção (ex: subopt_01)")
):
    try:
        available_subs = await get_available_suboptions(section_opcao=CURRENT_SECTION_OPCAO)
        if not any(sub['value'] == subopcao_value for sub in available_subs):
            raise HTTPException(status_code=404, detail=f"Subopção '{subopcao_value}' não encontrada para {SECTION_NAME_PT}.")
        return await fetch_embrapa_data(section_opcao=CURRENT_SECTION_OPCAO, subopcao_value=subopcao_value, all_years=True)
    except HTTPException as http_exc:
        raise http_exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Falha ao buscar todos os dados para {SECTION_NAME_PT}/{subopcao_value}: {str(exc)}")

@router.get("/{subopcao_value}/year/{year}",
            summary=f"Obtém dados de uma subopção de {SECTION_NAME_PT} para um ano específico",
            description=f"Retorna dados para uma subopção específica de {SECTION_NAME_PT} e para um ano específico. O ano deve estar dentro do intervalo disponível para a subopção.",
            response_model=Dict[str, List[Dict[str, Any]]])
async def get_suboption_by_year_route(
    subopcao_value: str = Path(..., title="Valor da Subopção"),
    year: int = Path(..., title="Ano")
):
    try:
        available_subs = await get_available_suboptions(section_opcao=CURRENT_SECTION_OPCAO)
        if not any(sub['value'] == subopcao_value for sub in available_subs):
            raise HTTPException(status_code=404, detail=f"Subopção '{subopcao_value}' não encontrada para {SECTION_NAME_PT}.")

        min_year, max_year = await get_year_range(section_opcao=CURRENT_SECTION_OPCAO, subopcao_value=subopcao_value)
        if min_year is None or max_year is None:
            raise HTTPException(status_code=404, detail=f"Não foi possível determinar o intervalo de anos para {SECTION_NAME_PT}/{subopcao_value}.")
        if not (min_year <= year <= max_year):
            raise HTTPException(
                status_code=400,
                detail=f"Ano {year} fora do intervalo para {SECTION_NAME_PT}/{subopcao_value}. Intervalo disponível: [{min_year}-{max_year}]"
            )
        return await fetch_embrapa_data(section_opcao=CURRENT_SECTION_OPCAO, subopcao_value=subopcao_value, year_to_fetch=year)
    except HTTPException as http_exc:
        raise http_exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Falha ao buscar dados para {SECTION_NAME_PT}/{subopcao_value} ano {year}: {str(exc)}")

@router.get("/{subopcao_value}",
            summary=f"Obtém dados de uma subopção de {SECTION_NAME_PT} do último ano disponível",
            description=f"Retorna dados para uma subopção específica de {SECTION_NAME_PT}, referentes ao ano mais recente com dados disponíveis para essa subopção.",
            response_model=Dict[str, List[Dict[str, Any]]])
async def get_suboption_latest_year_route(
    subopcao_value: str = Path(..., title="Valor da Subopção")
):
    try:
        available_subs = await get_available_suboptions(section_opcao=CURRENT_SECTION_OPCAO)
        if not any(sub['value'] == subopcao_value for sub in available_subs):
            raise HTTPException(status_code=404, detail=f"Subopção '{subopcao_value}' não encontrada para {SECTION_NAME_PT}.")

        _, max_year = await get_year_range(section_opcao=CURRENT_SECTION_OPCAO, subopcao_value=subopcao_value)
        if max_year is None:
            raise HTTPException(status_code=404, detail=f"Não foi possível determinar o último ano para {SECTION_NAME_PT}/{subopcao_value}.")
        return await fetch_embrapa_data(section_opcao=CURRENT_SECTION_OPCAO, subopcao_value=subopcao_value, year_to_fetch=max_year)
    except HTTPException as http_exc:
        raise http_exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Falha ao buscar os dados mais recentes para {SECTION_NAME_PT}/{subopcao_value}: {str(exc)}")