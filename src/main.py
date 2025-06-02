from fastapi import FastAPI, Depends
from .api.routes import router
from .auth.security import oauth2_scheme, api_key_header_scheme, ensure_authenticated

openapi_components = {
    "securitySchemes": {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "auth/login",
                    "scopes": {}
                }
            }
        },
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Insira o token JWT Bearer completo aqui. Exemplo: \"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...\""
        }
    }
}

app = FastAPI(
    title="Web-Scraper API Embrapa",
    openapi_components=openapi_components,
)

app.include_router(router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)