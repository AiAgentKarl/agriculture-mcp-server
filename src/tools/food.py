"""Food-Tools — Lebensmittel-Datenbank (Open Food Facts)."""

from mcp.server.fastmcp import FastMCP
from src.clients.openfoodfacts import OpenFoodFactsClient

_off = OpenFoodFactsClient()


def register_food_tools(mcp: FastMCP):

    @mcp.tool()
    async def food_product_lookup(barcode: str) -> dict:
        """Lebensmittel per Barcode nachschlagen.

        Zeigt Nährwerte, Nutri-Score, Eco-Score und NOVA-Gruppe.
        Quelle: Open Food Facts (3+ Millionen Produkte).

        Args:
            barcode: EAN/UPC Barcode (z.B. "3017620422003" für Nutella)
        """
        data = await _off.get_product(barcode)
        product = data.get("product", {})

        if not product:
            return {"error": f"Produkt mit Barcode {barcode} nicht gefunden"}

        nutriments = product.get("nutriments", {})

        return {
            "barcode": product.get("code", barcode),
            "name": product.get("product_name", ""),
            "marke": product.get("brands", ""),
            "nutriscore": product.get("nutriscore_grade", ""),
            "ecoscore": product.get("ecoscore_grade", ""),
            "nova_gruppe": product.get("nova_group", ""),
            "naehrwerte_pro_100g": {
                "energie_kcal": nutriments.get("energy-kcal_100g"),
                "fett_g": nutriments.get("fat_100g"),
                "kohlenhydrate_g": nutriments.get("carbohydrates_100g"),
                "zucker_g": nutriments.get("sugars_100g"),
                "protein_g": nutriments.get("proteins_100g"),
                "salz_g": nutriments.get("salt_100g"),
                "ballaststoffe_g": nutriments.get("fiber_100g"),
            },
        }

    @mcp.tool()
    async def food_search(
        query: str, category: str = "", limit: int = 10,
    ) -> dict:
        """Lebensmittel suchen nach Name oder Kategorie.

        Args:
            query: Suchbegriff (z.B. "organic rice", "chocolate")
            category: Kategorie-Filter (z.B. "cereals", "dairy", "beverages")
            limit: Max. Ergebnisse (1-50)
        """
        data = await _off.search_products(
            query, page_size=min(limit, 50), category=category or None,
        )
        products = data.get("products", [])

        items = []
        for p in products:
            items.append({
                "barcode": p.get("code", ""),
                "name": p.get("product_name", ""),
                "marke": p.get("brands", ""),
                "nutriscore": p.get("nutriscore_grade", ""),
                "ecoscore": p.get("ecoscore_grade", ""),
            })

        return {
            "suchbegriff": query,
            "anzahl_treffer": data.get("count", 0),
            "produkte": items,
        }
