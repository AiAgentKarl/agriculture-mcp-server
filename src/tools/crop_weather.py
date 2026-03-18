"""Crop Weather Tools — Agrar-relevante Wetterdaten und Klima-Historie."""

from mcp.server.fastmcp import FastMCP
from src.clients.openmeteo import OpenMeteoClient
from src.clients.nasa_power import NasaPowerClient

_meteo = OpenMeteoClient()
_nasa = NasaPowerClient()


def register_crop_weather_tools(mcp: FastMCP):

    @mcp.tool()
    async def crop_weather_forecast(
        lat: float, lon: float, days: int = 7,
    ) -> dict:
        """Agrar-Wetter-Vorhersage für einen Standort.

        Zeigt Temperatur, Niederschlag, Wind, Sonnenstrahlung und
        Evapotranspiration — optimiert für Landwirtschaft und Pflanzenbau.

        Args:
            lat: Breitengrad
            lon: Längengrad
            days: Vorhersage-Tage (1-16)
        """
        data = await _meteo.get_crop_weather(lat, lon, days)
        daily = data.get("daily", {})
        times = daily.get("time", [])

        tage = []
        for i, date in enumerate(times):
            tage.append({
                "datum": date,
                "temp_max_c": daily.get("temperature_2m_max", [None])[i],
                "temp_min_c": daily.get("temperature_2m_min", [None])[i],
                "niederschlag_mm": daily.get("precipitation_sum", [None])[i],
                "niederschlag_stunden": daily.get("precipitation_hours", [None])[i],
                "wind_max_km_h": daily.get("wind_speed_10m_max", [None])[i],
                "strahlung_mj_m2": daily.get("shortwave_radiation_sum", [None])[i],
                "et0_mm": daily.get("et0_fao_evapotranspiration", [None])[i],
            })

        # Wasserbilanz berechnen (Niederschlag - Evapotranspiration)
        total_rain = sum(t["niederschlag_mm"] or 0 for t in tage)
        total_et0 = sum(t["et0_mm"] or 0 for t in tage)

        return {
            "standort": {"lat": data.get("latitude"), "lon": data.get("longitude")},
            "vorhersage": tage,
            "zusammenfassung": {
                "niederschlag_gesamt_mm": round(total_rain, 1),
                "evapotranspiration_gesamt_mm": round(total_et0, 1),
                "wasserbilanz_mm": round(total_rain - total_et0, 1),
                "bewaesserung_noetig": total_rain < total_et0,
            },
        }

    @mcp.tool()
    async def climate_history(
        lat: float, lon: float, start_date: str, end_date: str,
    ) -> dict:
        """Historische Agrar-Klimadaten für einen Standort (NASA POWER, ab 1981).

        Zeigt Temperatur, Niederschlag, Solarstrahlung, Bodenfeuchtigkeit und
        Evapotranspiration. Perfekt für Standortbewertung und Klimaanalyse.

        Args:
            lat: Breitengrad
            lon: Längengrad
            start_date: Startdatum (YYYYMMDD, z.B. "20240601")
            end_date: Enddatum (YYYYMMDD, z.B. "20240630")
        """
        data = await _nasa.get_daily(lat, lon, start_date, end_date)
        props = data.get("properties", {})
        params = props.get("parameter", {})

        # Daten in lesbares Format umwandeln
        dates = sorted(params.get("T2M", {}).keys()) if params.get("T2M") else []

        tage = []
        for date in dates:
            tag = {"datum": date}
            for param_name, values in params.items():
                val = values.get(date)
                if val is not None and val != -999:
                    tag[param_name.lower()] = val
            tage.append(tag)

        # Parameter-Beschreibungen
        param_info = data.get("parameters", {})

        return {
            "standort": {"lat": lat, "lon": lon},
            "zeitraum": f"{start_date} bis {end_date}",
            "anzahl_tage": len(tage),
            "daten": tage,
            "parameter_info": {
                k: v.get("longname", "") for k, v in param_info.items()
            },
        }

    @mcp.tool()
    async def climate_averages(lat: float, lon: float) -> dict:
        """Langjährige Klimamittelwerte für einen Standort (NASA POWER).

        Zeigt monatliche Durchschnittswerte für Temperatur, Niederschlag,
        Solarstrahlung und Bodenfeuchtigkeit (2001-2020).
        Ideal zur Standortbewertung für neue Anbauflächen.

        Args:
            lat: Breitengrad
            lon: Längengrad
        """
        data = await _nasa.get_climatology(lat, lon)
        props = data.get("properties", {})
        params = props.get("parameter", {})

        monate_namen = [
            "Jan", "Feb", "Mär", "Apr", "Mai", "Jun",
            "Jul", "Aug", "Sep", "Okt", "Nov", "Dez",
        ]

        monate = []
        for i in range(1, 13):
            key = str(i).zfill(2)
            monat = {"monat": monate_namen[i - 1]}
            for param_name, values in params.items():
                val = values.get(key)
                if val is not None and val != -999:
                    monat[param_name.lower()] = val
            monate.append(monat)

        # Jahresmittel
        jahres = {}
        for param_name, values in params.items():
            ann = values.get("13") or values.get("ANN")
            if ann is not None and ann != -999:
                jahres[param_name.lower()] = ann

        return {
            "standort": {"lat": lat, "lon": lon},
            "zeitraum": "2001-2020",
            "monatsmittel": monate,
            "jahresmittel": jahres,
        }
