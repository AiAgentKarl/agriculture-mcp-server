"""Open Food Facts Client — Lebensmittel-Datenbank (Nährwerte, Eco-Scores)."""

import httpx
from src.config import settings


# Standard-Felder für Suchanfragen
DEFAULT_FIELDS = "code,product_name,brands,nutriscore_grade,ecoscore_grade,nova_group,nutriments,categories_tags_en"


class OpenFoodFactsClient:
    """Async-Client für Open Food Facts. Kein Key nötig."""

    def __init__(self):
        self._client = httpx.AsyncClient(
            timeout=settings.http_timeout,
            headers={"User-Agent": "AgricultureMCP/0.1 (AI-Agent-Tool)"},
        )
        self._base = settings.openfoodfacts_base_url

    async def get_product(self, barcode: str) -> dict:
        """Produkt per Barcode abrufen."""
        resp = await self._client.get(
            f"{self._base}/api/v2/product/{barcode}",
            params={"fields": DEFAULT_FIELDS},
        )
        resp.raise_for_status()
        return resp.json()

    async def search_products(
        self, query: str, page_size: int = 10, category: str | None = None,
    ) -> dict:
        """Produkte suchen nach Text oder Kategorie."""
        params = {
            "fields": DEFAULT_FIELDS,
            "page_size": min(page_size, 50),
            "sort_by": "unique_scans_n",
        }
        if category:
            params["categories_tags_en"] = category
        if query:
            params["search_terms"] = query

        resp = await self._client.get(
            f"{self._base}/cgi/search.pl",
            params={**params, "search_simple": 1, "action": "process", "json": 1},
        )
        resp.raise_for_status()
        return resp.json()

    async def close(self):
        await self._client.aclose()
