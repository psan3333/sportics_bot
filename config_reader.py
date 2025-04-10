from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    BOT_TOKEN: SecretStr
    DATABASE_URL: SecretStr
    DONATIONS_URL: SecretStr
    ADMIN_ID: SecretStr
    model_config: SettingsConfigDict = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8'
    )


config = Settings()
