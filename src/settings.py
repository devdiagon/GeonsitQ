from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
  model_config = SettingsConfigDict(env_file=BASE_DIR / ".env")
  CITY: str
  COUNTRY: str
  DISTRICTS: list[str]
  SHP_METRO: str
  SHP_METRO_STATIONS: str
  SHP_BUS_ROUTES: str
  SHP_BUS_STOPS: str
  SHP_CRIMES: str

settings = Settings()