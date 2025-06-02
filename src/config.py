from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "webscraper-embrapa"
    ENVIRONMENT: str = "dev"
    LOG_LEVEL: str = "INFO"

    TARGET_BASE_URL: str
    USER_AGENT: Optional[str] = None
    TIMEOUT: int = 30
    SCRAPER_MAX_CONCURRENCY: int = 5
    SCRAPER_RETRY_ATTEMPTS: int = 3

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    AUTH_SERVICE_URL: str = "https://authentication-x2ug.onrender.com/"

    AZURE_TENANT_ID: Optional[str] = None
    AZURE_CLIENT_ID: Optional[str] = None
    AZURE_CLIENT_SECRET: Optional[str] = None

    EH_CONN_STR: Optional[str] = None
    EH_NAME: Optional[str] = "vinhos-requests"
    EH_CONSUMER_GROUP: str = "$Default"

    TABLE_CONN_STR: Optional[str] = None
    TABLE_NAME: Optional[str] = "ScraperStatus"
    BLOB_CONN_STR: Optional[str] = None
    BLOB_CONTAINER: Optional[str] = "raw-pages"
    SQL_SERVER: Optional[str] = None
    SQL_DATABASE: Optional[str] = "EmbrapaVitiviniculturaScrapper"
    SQL_USERNAME: Optional[str] = None
    SQL_PASSWORD: Optional[str] = None
    SQL_ENCRYPT: bool = True
    SQL_DRIVER: Optional[str] = "{ODBC Driver 18 for SQL Server}"

    APPINSIGHTS_CONNECTION_STRING: Optional[str] = None
    KEYVAULT_URI: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra='ignore'
    )

settings = Settings()