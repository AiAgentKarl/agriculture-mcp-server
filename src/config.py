"""Konfiguration — API-URLs und optionale Keys."""

import os
from pathlib import Path
from dotenv import load_dotenv

_project_root = Path(__file__).resolve().parent.parent
_env_path = _project_root / "keys.env"
if not _env_path.exists():
    _env_path = _project_root / ".env"
load_dotenv(_env_path)


class Settings:
    """Zentrale Konfiguration. Alle APIs kostenlos, USDA braucht optionalen Free-Key."""

    # Open-Meteo (Agri-Wetter, Boden, Evapotranspiration)
    openmeteo_base_url: str = "https://api.open-meteo.com/v1"
    openmeteo_geocoding_url: str = "https://geocoding-api.open-meteo.com/v1"

    # NASA POWER (Historisches Agri-Klima)
    nasa_power_base_url: str = "https://power.larc.nasa.gov/api/temporal"

    # World Bank (Globale Agrar-Statistiken)
    worldbank_base_url: str = "https://api.worldbank.org/v2"

    # Open Food Facts (Lebensmittel-Datenbank)
    openfoodfacts_base_url: str = "https://world.openfoodfacts.net"

    # USDA NASS QuickStats (US Crop Data — optionaler Free-Key)
    usda_api_key: str = os.getenv("USDA_API_KEY", "")
    usda_base_url: str = "https://quickstats.nass.usda.gov/api"

    http_timeout: float = 30.0


settings = Settings()
