import os
import requests
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from starlette.responses import PlainTextResponse

# Task 2: Implement World Data MCP Server
# Task 3: Implement Weather MCP Tool and Run the Server

load_dotenv()

mcp = FastMCP("World Data Server", port=8001)

@mcp.custom_route("/", methods=["GET"])
async def index(request=None):
    return PlainTextResponse("World Data MCP Server is running! Use /sse to connect.")


@mcp.tool()
def search_news(query: str) -> dict:
    """Search for news articles using the News API."""
    api_key = os.getenv("NEWSAPI_KEY")
    if not api_key:
        return {"error": "NEWSAPI_KEY is not set in environment variables."}

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "apiKey": api_key,
        "pageSize": 1,
        "sortBy": "relevancy"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if not data.get("articles"):
            return {"error": "No news articles found for the given query."}
            
        first_article = data["articles"][0]
        
        return {
            "headline": first_article.get("title"),
            "description": first_article.get("description"),
            "source": first_article.get("source", {}).get("name"),
            "url": first_article.get("url"),
            "published_date": first_article.get("publishedAt")
        }
        
    except requests.exceptions.RequestException as e:
        return {"error": f"HTTP error occurred: {str(e)}"}

@mcp.tool()
def get_weather(city: str, units: str = "metric") -> dict:
    """Get the current weather for a city."""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return {"error": "OPENWEATHER_API_KEY is not set in environment variables."}

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": units
    }

    try:
        response = requests.get(url, params=params)
        
        # Handle specific HTTP errors
        if response.status_code == 401:
            return {"error": "Invalid OpenWeather API Key (401 Unauthorized)."}
        if response.status_code == 404:
            return {"error": f"City '{city}' not found (404 Not Found)."}
            
        # Raise for any other HTTP errors
        response.raise_for_status()
        
        data = response.json()
        
        # Extract fields
        main = data.get("main", {})
        weather_list = data.get("weather", [])
        weather_description = weather_list[0].get("description") if weather_list else "Unknown"
        
        return {
            "temperature": main.get("temp"),
            "humidity": main.get("humidity"),
            "description": weather_description,
            "city": data.get("name"),
            "country": data.get("sys", {}).get("country")
        }
        
    except requests.exceptions.RequestException as e:
        return {"error": f"HTTP error occurred: {str(e)}"}

if __name__ == "__main__":
    mcp.run(transport="sse")
