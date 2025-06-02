from fastapi import FastAPI
from .api.routes import router
from .auth.security import PROXY_LOGIN_ENDPOINT_FULL_PATH

openapi_components = {
    "securitySchemes": {
        "OAuth2PasswordBearerProxy": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": PROXY_LOGIN_ENDPOINT_FULL_PATH,
                    "scopes": {}
                }
            }
        }
    }
}

app = FastAPI(
    title="Web-Scraper API Embrapa",
    openapi_components=openapi_components
)

app.include_router(router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)