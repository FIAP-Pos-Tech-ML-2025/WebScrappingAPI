from fastapi import APIRouter, Query, HTTPException
from ..scraper.core import fetch

router = APIRouter()

@router.get("/scrape")
async def scrape(query: str = Query(...)):
    try:
        return await fetch(query)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))