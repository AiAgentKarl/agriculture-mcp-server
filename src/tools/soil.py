"""Boden-Tools — Bodentemperatur, Feuchtigkeit, Evapotranspiration."""

from mcp.server.fastmcp import FastMCP
from src.clients.openmeteo import OpenMeteoClient

_meteo = OpenMeteoClient()


def register_soil_tools(mcp: FastMCP):

    @mcp.tool()
    async def soil_conditions(
        lat: float, lon: float, days: int = 7,
    ) -> dict:
        """Aktuelle und prognostizierte Bodenbedingungen für einen Standort.

        Zeigt Bodentemperatur (0-54cm Tiefe), Bodenfeuchtigkeit und
        FAO-Evapotranspiration. Ideal für Aussaat-Entscheidungen und
        Bewässerungsplanung.

        Args:
            lat: Breitengrad (z.B. 52.52 für Berlin)
            lon: Längengrad (z.B. 13.41 für Berlin)
            days: Vorhersage-Tage (1-16, Standard: 7)
        """
        data = await _meteo.get_soil_forecast(lat, lon, days)
        daily = data.get("daily", {})
        times = daily.get("time", [])

        tage = []
        for i, date in enumerate(times):
            tage.append({
                "datum": date,
                "temp_max_c": daily.get("temperature_2m_max", [None])[i],
                "temp_min_c": daily.get("temperature_2m_min", [None])[i],
                "niederschlag_mm": daily.get("precipitation_sum", [None])[i],
                "evapotranspiration_mm": daily.get("et0_fao_evapotranspiration", [None])[i],
                "strahlung_mj_m2": daily.get("shortwave_radiation_sum", [None])[i],
            })

        # Aktuellste stündliche Bodenwerte
        hourly = data.get("hourly", {})
        hourly_temps = hourly.get("soil_temperature_0cm", [])
        hourly_moisture = hourly.get("soil_moisture_0_to_1cm", [])

        aktuell = {}
        if hourly_temps:
            aktuell["bodentemp_oberflaeche_c"] = hourly_temps[0]
        if hourly_moisture:
            aktuell["bodenfeuchtigkeit_m3_m3"] = hourly_moisture[0]

        deep_temps = hourly.get("soil_temperature_54cm", [])
        deep_moisture = hourly.get("soil_moisture_27_to_81cm", [])
        if deep_temps:
            aktuell["bodentemp_54cm_c"] = deep_temps[0]
        if deep_moisture:
            aktuell["bodenfeuchtigkeit_27_81cm_m3_m3"] = deep_moisture[0]

        return {
            "standort": {"lat": data.get("latitude"), "lon": data.get("longitude"),
                         "elevation_m": data.get("elevation")},
            "aktueller_boden": aktuell,
            "tages_vorhersage": tage,
        }
