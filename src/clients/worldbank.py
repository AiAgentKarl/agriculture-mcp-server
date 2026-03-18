"""World Bank Client — Globale Agrar-Statistiken nach Land."""

import httpx
from src.config import settings


# Wichtigste Agrar-Indikatoren
AGRI_INDICATORS = {
    "cereal_yield": "AG.YLD.CREL.KG",
    "cereal_production": "AG.PRD.CREL.MT",
    "arable_land_pct": "AG.LND.ARBL.ZS",
    "arable_land_ha": "AG.LND.ARBL.HA",
    "agricultural_land_pct": "AG.LND.AGRI.ZS",
    "crop_production_index": "AG.PRD.CROP.XD",
    "food_production_index": "AG.PRD.FOOD.XD",
    "livestock_production_index": "AG.PRD.LVSK.XD",
    "fertilizer_consumption": "AG.CON.FERT.ZS",
    "agriculture_gdp_pct": "NV.AGR.TOTL.ZS",
    "agriculture_employment_pct": "SL.AGR.EMPL.ZS",
    "water_agriculture_pct": "ER.H2O.FWAG.ZS",
    "food_insecurity_pct": "SN.ITK.MSFI.ZS",
    "precipitation_mm": "AG.LND.PRCP.MM",
}


class WorldBankClient:
    """Async-Client für World Bank API. Kein Key nötig."""

    def __init__(self):
        self._client = httpx.AsyncClient(timeout=settings.http_timeout)
        self._base = settings.worldbank_base_url

    async def get_indicator(
        self, country: str, indicator_id: str,
        date_range: str = "2015:2023",
    ) -> list[dict]:
        """Einen Indikator für ein Land abrufen.

        Args:
            country: ISO3-Code (z.B. "DEU", "USA", "BRA") oder mehrere mit ";"
            indicator_id: World Bank Indicator ID
            date_range: Zeitbereich (z.B. "2020" oder "2015:2023")
        """
        resp = await self._client.get(
            f"{self._base}/country/{country}/indicator/{indicator_id}",
            params={"format": "json", "date": date_range, "per_page": 100},
        )
        resp.raise_for_status()
        data = resp.json()
        # World Bank gibt [metadata, data] zurück
        if isinstance(data, list) and len(data) > 1:
            return data[1] or []
        return []

    async def get_country_agri_profile(self, country: str) -> dict:
        """Komplettes Agrar-Profil eines Landes (alle Indikatoren)."""
        results = {}
        for name, indicator_id in AGRI_INDICATORS.items():
            try:
                data = await self.get_indicator(country, indicator_id, "2022")
                # Neuesten nicht-None-Wert nehmen
                value = None
                year = None
                for entry in data:
                    if entry and entry.get("value") is not None:
                        value = entry["value"]
                        year = entry.get("date")
                        break
                results[name] = {"value": value, "year": year}
            except Exception:
                results[name] = {"value": None, "error": "nicht verfügbar"}
        return results

    async def close(self):
        await self._client.aclose()
