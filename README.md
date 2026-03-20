# Agriculture MCP Server

MCP server providing AI agents with agriculture and farming data — soil conditions, crop weather, climate history, global statistics, and food products.

[![agriculture-mcp-server MCP server](https://glama.ai/mcp/servers/AiAgentKarl/agriculture-mcp-server/badges/card.svg)](https://glama.ai/mcp/servers/AiAgentKarl/agriculture-mcp-server)

## 8 Tools in 4 Categories

### Soil Conditions
- `soil_conditions` — Soil temperature (0-54cm), moisture, evapotranspiration forecast

### Crop Weather
- `crop_weather_forecast` — Agricultural weather: temp, rain, wind, radiation, water balance
- `climate_history` — Historical daily climate data since 1981 (NASA POWER)
- `climate_averages` — Long-term monthly climate averages for site assessment

### Global Statistics (World Bank)
- `country_agriculture_profile` — Full agriculture profile of any country
- `compare_countries` — Compare agriculture indicators across countries

### Food Products (Open Food Facts)
- `food_product_lookup` — Look up food products by barcode (nutrition, eco-scores)
- `food_search` — Search 3M+ food products by name or category

## Installation

```bash
pip install agriculture-mcp-server
```

## Usage with Claude Code

`.mcp.json`:

```json
{
  "mcpServers": {
    "agriculture": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "src.server"]
    }
  }
}
```

## Data Sources

All APIs are **free and require no API key**:

| API | Data |
|-----|------|
| Open-Meteo | Soil temperature, moisture, evapotranspiration, crop weather |
| NASA POWER | Historical climate data since 1981 (agricultural community) |
| World Bank | Country-level agriculture statistics (20+ indicators) |
| Open Food Facts | 3M+ food products with nutrition and eco-scores |

## License

MIT