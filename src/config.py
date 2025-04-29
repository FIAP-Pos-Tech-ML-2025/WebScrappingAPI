from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "webscraper-embrapa"
    ENVIRONMENT: str = "dev"
    LOG_LEVEL: str = "INFO"

    TARGET_BASE_URL: str
    USER_AGENT: str
    TIMEOUT: int = 10
    SCRAPER_MAX_CONCURRENCY: int = 5
    SCRAPER_RETRY_ATTEMPTS: int = 3

    AZURE_TENANT_ID: str | None = None
    AZURE_CLIENT_ID: str | None = None
    AZURE_CLIENT_SECRET: str | None = None

    EH_CONN_STR: str
    EH_NAME: str
    EH_CONSUMER_GROUP: str = "$Default"

    TABLE_CONN_STR: str
    TABLE_NAME: str

    BLOB_CONN_STR: str
    BLOB_CONTAINER: str

    SQL_SERVER: str
    SQL_DATABASE: str
    SQL_USERNAME: str
    SQL_PASSWORD: str
    SQL_ENCRYPT: bool = True
    SQL_DRIVER: str

    APPINSIGHTS_CONNECTION_STRING: str | None = None
    KEYVAULT_URI: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

settings = Settings()
