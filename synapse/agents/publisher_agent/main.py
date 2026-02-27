import os
import json
from mcp.server.fastmcp import FastMCP
from openai import OpenAI
from dotenv import load_dotenv
from starlette.responses import PlainTextResponse

# Task 9: Build Publisher Agent to Generate Articles

load_dotenv()

mcp = FastMCP("Publisher Agent", port=8005)

@mcp.custom_route("/", methods=["GET"])
async def index(request=None):
    return PlainTextResponse("Publisher Agent MCP Server is running! Use /sse to connect.")

@mcp.tool()
def publish_brief(payload: dict) -> dict:
    """
    Generate a journalistic daily brief article using OpenAI based on aggregated signals.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {"error": "OPENAI_API_KEY is not set in environment variables."}

    client = OpenAI(api_key=api_key)

    topic = payload.get("topic", "N/A")
    city = payload.get("city", "N/A")
    context = payload.get("context", {})
    media = payload.get("media", {})

    prompt = f"""
    Write a neutral, journalistic daily brief article based strictly on the following data:

    Topic: {topic}
    City: {city}
    
    Contextual Data:
    - News: {json.dumps(context.get('news_context', {}))}
    - Weather: {json.dumps(context.get('weather_context', {}))}
    - Financial (FX Rate): {json.dumps(context.get('financial_context', {}))}
    
    Media Data:
    - Images: {json.dumps(media.get('images', []))}

    The article should include the following sections clearly:
    1. A catchy Headline.
    2. A summary paragraph of the main news.
    3. A "Why it matters" section explaining the significance.
    4. A "Local Context" section including weather and financial info for {city}.
    5. A mention of available media assets.

    Maintain a professional and informative tone.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a professional journalist writing daily briefs."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )

        article_text = response.choices[0].message.content

        return {
            "topic": topic,
            "city": city,
            "article": article_text,
            "original_payload": payload
        }

    except Exception as e:
        return {"error": f"Failed to generate article: {str(e)}"}

if __name__ == "__main__":
    mcp.run(transport="sse")