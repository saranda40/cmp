from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    PROJECT_NAME: str = "CMP API"

    # Permite leer desde el archivo .env automáticamente
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()