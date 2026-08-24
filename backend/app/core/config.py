from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Mandalan API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False

    DATABASE_URL: str = "mysql+aiomysql://mandalan:mandalan@db:3318/mandalan"

    CORS_ORIGINS: list[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
