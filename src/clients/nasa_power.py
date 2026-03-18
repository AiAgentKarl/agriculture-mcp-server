"""NASA POWER Client — Historische Agrar-Klimadaten (ab 1981)."""

import httpx
from src.config import settings


# Wichtigste Agrar-Parameter
AGRI_PARAMS = [
    "T2M", "T2M_MAX", "T2M_MIN",  # Temperatur
    "PRECTOTCORR",                  # Niederschlag
    "ALLSKY_SFC_SW_DWN",            # Solarstrahlung
    "RH2M",                         # Luftfeuchtigkeit
    "WS2M",                         # Wind
    "GWETROOT",                     # Root Zone Soil Wetness
    "GWETPROF",                     # Profile Soil Moisture
    "EVPTRNS",                      # Evapotranspiration
]


class NasaPowerClient:
    """Async-Client für NASA POWER API. Kein Key nötig."""

    def __init__(self):
        self._client = httpx.AsyncClient(timeout=settings.http_timeout)
        self._base = settings.nasa_power_base_url

    async def get_daily(
        self, lat: float, lon: float, start: str, end: str,
        params: list[str] | None = None,
    ) -> dict:
        """Tägliche Agrar-Klimadaten für einen Punkt.

        Args:
            lat/lon: Koordinaten
            start/end: Format YYYYMMDD (z.B. "20240601")
            params: NASA POWER Parameter (default: alle Agrar-Parameter)
        """
        if params is None:
            params = AGRI_PARAMS
        resp = await self._client.get(
            f"{self._base}/daily/point",
            params={
                "parameters": ",".join(params),
                "community": "AG",
                "latitude": lat,
                "longitude": lon,
                "start": start,
                "end": end,
                "format": "JSON",
            },
        )
        resp.raise_for_status()
        return resp.json()

    async def get_climatology(
        self, lat: float, lon: float,
        start_year: int = 2001, end_year: int = 2020,
    ) -> dict:
        """Monatliche Klimamittelwerte (Climatology) für einen Punkt."""
        resp = await self._client.get(
            f"{self._base}/climatology/point",
            params={
                "parameters": "T2M,PRECTOTCORR,ALLSKY_SFC_SW_DWN,RH2M,GWETROOT",
                "community": "AG",
                "latitude": lat,
                "longitude": lon,
                "start": start_year,
                "end": end_year,
                "format": "JSON",
            },
        )
        resp.raise_for_status()
        return resp.json()

    async def close(self):
        await self._client.aclose()
