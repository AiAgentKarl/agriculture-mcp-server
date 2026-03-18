"""Open-Meteo Client — Agrar-Wetter, Bodendaten, Evapotranspiration."""

import httpx
from src.config import settings


class OpenMeteoClient:
    """Async-Client für Open-Meteo API. Kein Key nötig."""

    def __init__(self):
        self._client = httpx.AsyncClient(timeout=settings.http_timeout)
        self._base = settings.openmeteo_base_url
        self._geo = settings.openmeteo_geocoding_url

    async def get_soil_forecast(self, lat: float, lon: float, days: int = 7) -> dict:
        """Bodentemperatur, Bodenfeuchtigkeit und ET0 Vorhersage."""
        resp = await self._client.get(
            f"{self._base}/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "hourly": ",".join([
                    "soil_temperature_0cm", "soil_temperature_6cm",
                    "soil_temperature_18cm", "soil_temperature_54cm",
                    "soil_moisture_0_to_1cm", "soil_moisture_1_to_3cm",
                    "soil_moisture_3_to_9cm", "soil_moisture_9_to_27cm",
                    "soil_moisture_27_to_81cm", "et0_fao_evapotranspiration",
                ]),
                "daily": ",".join([
                    "et0_fao_evapotranspiration", "temperature_2m_max",
                    "temperature_2m_min", "precipitation_sum",
                    "shortwave_radiation_sum",
                ]),
                "timezone": "auto",
                "forecast_days": min(days, 16),
            },
        )
        resp.raise_for_status()
        return resp.json()

    async def get_crop_weather(self, lat: float, lon: float, days: int = 7) -> dict:
        """Agrar-relevante Wetterdaten (Temp, Regen, Wind, Strahlung)."""
        resp = await self._client.get(
            f"{self._base}/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "daily": ",".join([
                    "temperature_2m_max", "temperature_2m_min",
                    "precipitation_sum", "precipitation_hours",
                    "wind_speed_10m_max", "shortwave_radiation_sum",
                    "et0_fao_evapotranspiration",
                ]),
                "timezone": "auto",
                "forecast_days": min(days, 16),
            },
        )
        resp.raise_for_status()
        return resp.json()

    async def geocode(self, name: str, count: int = 5) -> list[dict]:
        """Ortsname in Koordinaten umwandeln."""
        resp = await self._client.get(
            f"{self._geo}/search",
            params={"name": name, "count": count, "language": "en", "format": "json"},
        )
        resp.raise_for_status()
        return resp.json().get("results", [])

    async def close(self):
        await self._client.aclose()
