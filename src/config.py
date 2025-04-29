from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    TARGET_BASE_URL: str
    USER_AGENT: str = "MyScraperBot/1.0"
    TIMEOUT: int = 10

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
