import os
import requests
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from starlette.responses import PlainTextResponse

# Task 5: Implement Media Engine MCP Server

load_dotenv()

mcp = FastMCP("Media Engine", port=8003)

PEXELS_SEARCH_URL = "https://api.pexels.com/v1/search"

@mcp.custom_route("/", methods=["GET"])
async def index(request=None):
    return PlainTextResponse("Media Engine MCP Server is running! Use /sse to connect.")

@mcp.tool()
def search_images(query: str, count: int = 1) -> dict:
    """
    Search for high-quality images using the Pexels API.
    """
    api_key = os.getenv("PEXELS_API_KEY")
    if not api_key:
        return {"error": "PEXELS_API_KEY is not set in environment variables."}

    headers = {
        "Authorization": api_key
    }
    
    params = {
        "query": query,
        "per_page": count
    }

    try:
        response = requests.get(PEXELS_SEARCH_URL, headers=headers, params=params)
        
        if response.status_code == 401:
            return {"error": "Unauthorized: Invalid Pexels API Key."}
            
        response.raise_for_status()
        
        data = response.json()
        
        photos = data.get("photos", [])
        formatted_images = []
        
        for photo in photos:
            formatted_images.append({
                "id": photo.get("id"),
                "width": photo.get("width"),
                "height": photo.get("height"),
                "url": photo.get("url"),
                "photographer": photo.get("photographer"),
                "src": photo.get("src", {}).get("large"),
                "alt": photo.get("alt")
            })
            
        return {
            "query": query,
            "total_results": data.get("total_results"),
            "images": formatted_images
        }
        
    except requests.exceptions.HTTPError as e:
        return {"error": f"HTTP error occurred: {str(e)}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Request error occurred: {str(e)}"}

if __name__ == "__main__":
    mcp.run(transport="sse")
