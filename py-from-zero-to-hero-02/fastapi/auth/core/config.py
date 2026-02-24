from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    # Pydantic will Look for an environment variable named DATABASE_URL
    # If found it will be used otherwise it assumes default value
    DATABASE_URL: str = "postgresql+asyncpg://app:app@localhost:5432/inventorydb"

settings = Settings()