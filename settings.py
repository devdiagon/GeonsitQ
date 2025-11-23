from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
  model_config = SettingsConfigDict(env_file=".env")
  CITY: str
  COUNTRY: str
  DISTRICTS: list[str]

settings = Settings()