from fastapi import FastAPI
from .api.routes import router
import uvicorn

app = FastAPI(title="Web-Scraper API Embrapa")
app.include_router(router, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)