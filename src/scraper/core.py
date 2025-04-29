import httpx
from bs4 import BeautifulSoup
from ..config import settings

async def fetch(query: str) -> dict:
    url = f"{settings.TARGET_BASE_URL}/{query}"
    async with httpx.AsyncClient(
        headers={"User-Agent": settings.USER_AGENT},
        timeout=settings.TIMEOUT
    ) as client:
        r = await client.get(url)
        r.raise_for_status()

    soup = BeautifulSoup(r.text, "lxml")
    
    # ...extrair dados...
    
    return 0