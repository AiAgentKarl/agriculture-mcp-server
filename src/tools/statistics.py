"""Statistik-Tools — Globale Agrar-Statistiken (World Bank)."""

from mcp.server.fastmcp import FastMCP
from src.clients.worldbank import WorldBankClient, AGRI_INDICATORS

_wb = WorldBankClient()


def register_statistics_tools(mcp: FastMCP):

    @mcp.tool()
    async def country_agriculture_profile(country: str) -> dict:
        """Komplettes Agrar-Profil eines Landes.

        Zeigt Ernteerträge, Landnutzung, Produktionsindizes, Düngereinsatz,
        Agrar-Anteil am BIP und Beschäftigung. Quelle: World Bank.

        Args:
            country: ISO3-Ländercode (z.B. "DEU", "USA", "BRA", "IND", "CHN")
        """
        profile = await _wb.get_country_agri_profile(country.upper())

        return {
            "land": country.upper(),
            "profil": profile,
            "verfuegbare_indikatoren": list(AGRI_INDICATORS.keys()),
        }

    @mcp.tool()
    async def compare_countries(
        countries: str, indicator: str = "cereal_yield",
        year_range: str = "2018:2023",
    ) -> dict:
        """Agrar-Indikator zwischen Ländern vergleichen.

        Args:
            countries: Länder-Codes getrennt mit Semikolon (z.B. "DEU;USA;BRA;IND;CHN")
            indicator: Indikator-Name (z.B. "cereal_yield", "arable_land_pct",
                       "fertilizer_consumption", "agriculture_gdp_pct")
            year_range: Zeitbereich (z.B. "2020" oder "2018:2023")
        """
        indicator_id = AGRI_INDICATORS.get(indicator)
        if not indicator_id:
            return {
                "error": f"Unbekannter Indikator: {indicator}",
                "verfuegbare": list(AGRI_INDICATORS.keys()),
            }

        data = await _wb.get_indicator(countries.upper(), indicator_id, year_range)

        # Nach Land gruppieren
        by_country = {}
        for entry in data:
            if entry and entry.get("value") is not None:
                country_name = entry.get("country", {}).get("value", "")
                code = entry.get("countryiso3code", "")
                if code not in by_country:
                    by_country[code] = {"name": country_name, "werte": []}
                by_country[code]["werte"].append({
                    "jahr": entry.get("date"),
                    "wert": entry["value"],
                })

        return {
            "indikator": indicator,
            "indikator_id": indicator_id,
            "zeitraum": year_range,
            "laender": by_country,
        }
