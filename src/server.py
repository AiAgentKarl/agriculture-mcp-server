"""Agriculture MCP Server — Farming & AgTech data for AI Agents.

Combines 4 free APIs:
- Open-Meteo (soil conditions, crop weather)
- NASA POWER (historical agricultural climate, since 1981)
- World Bank (global agriculture statistics by country)
- Open Food Facts (food product database, 3M+ products)
"""

from mcp.server.fastmcp import FastMCP

from src.tools.soil import register_soil_tools
from src.tools.crop_weather import register_crop_weather_tools
from src.tools.statistics import register_statistics_tools
from src.tools.food import register_food_tools

mcp = FastMCP(
    "Agriculture MCP Server",
    instructions=(
        "Provides AI agents with agriculture and farming data: "
        "soil conditions, crop weather forecasts, climate history, "
        "global agriculture statistics, and food product information."
    ),
)

register_soil_tools(mcp)
register_crop_weather_tools(mcp)
register_statistics_tools(mcp)
register_food_tools(mcp)

if __name__ == "__main__":
    mcp.run()
