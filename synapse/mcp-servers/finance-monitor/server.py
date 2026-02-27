import os
import requests
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from starlette.responses import PlainTextResponse

# Task 4: Implement Finance MCP Server

load_dotenv()

mcp = FastMCP("Finance Monitor", port=8002)

@mcp.custom_route("/", methods=["GET"])
async def index(request=None):
    return PlainTextResponse("Finance Monitor MCP Server is running! Use /sse to connect.")

def get_currency_code(location: str) -> str:
    """
    Helper function to obtain the target currency code from a location.
    Maps common country names/locations to their ISO currency codes.
    """
    location_map = {
        "usa": "USD",
        "united states": "USD",
        "uk": "GBP",
        "united kingdom": "GBP",
        "london": "GBP",
        "europe": "EUR",
        "germany": "EUR",
        "france": "EUR",
        "japan": "JPY",
        "tokyo": "JPY",
        "canada": "CAD",
        "australia": "AUD",
        "india": "INR",
        "china": "CNY",
        "nigeria": "NGN",
        "lagos": "NGN"
    }
    
    # Normalize input
    key = location.lower().strip()
    return location_map.get(key, "USD") # Default to USD if location not found

@mcp.tool()
def get_fx_rate(location: str) -> dict:
    """
    Fetch the foreign exchange rate for a given location relative to USD.
    """
    api_key = os.getenv("EXCHANGE_RATE_API_KEY")
    if not api_key:
        return {"error": "EXCHANGE_RATE_API_KEY is not set in environment variables."}

    currency_code = get_currency_code(location)
    
    # Building the ExchangeRate API URL
    # Format: https://v6.exchangerate-api.com/v6/YOUR-API-KEY/pair/BASE/TARGET
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/USD/{currency_code}"

    try:
        response = requests.get(url)
        
        if response.status_code != 200:
            return {
                "error": f"Failed to fetch exchange rate. API returned status code {response.status_code}.",
                "details": response.text
            }
            
        data = response.json()
        
        if data.get("result") == "success":
            return {
                "base_code": "USD",
                "target_code": currency_code,
                "conversion_rate": data.get("conversion_rate"),
                "last_update": data.get("time_last_update_utc"),
                "location_queried": location
            }
        else:
            return {
                "error": "API returned an unsuccessful result.",
                "details": data.get("error-type", "Unknown error")
            }
            
    except requests.exceptions.RequestException as e:
        return {"error": f"HTTP error occurred: {str(e)}"}

if __name__ == "__main__":
    mcp.run(transport="sse")
