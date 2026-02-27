import asyncio
import json
from contextlib import AsyncExitStack
from mcp.server.fastmcp import FastMCP
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client
from synapse.protocol.post_office import send_message

# Task 7: Build Contextualist Agent to Fetch Contextual Data

# Define upstream service URLs
WORLD_DATA_URL = "http://127.0.0.1:8001/sse"
FINANCE_URL = "http://127.0.0.1:8002/sse"

mcp = FastMCP("Contextualist Agent", port=8000)

@mcp.tool()
async def contextualize(topic: str, city: str, task_id: str = "default_task") -> dict:
    """
    Gather news, weather, and financial context for a given topic and city.
    Connects to the World Data Server and Finance Monitor Server.
    """
    async with AsyncExitStack() as stack:
        try:
            # Connect to World Data Server (New & Weather)
            world_conn = await stack.enter_async_context(sse_client(WORLD_DATA_URL))
            world_session = await stack.enter_async_context(ClientSession(world_conn[0], world_conn[1]))
            await world_session.initialize()
            
            # Connect to Finance Monitor Server (FX Rate)
            finance_conn = await stack.enter_async_context(sse_client(FINANCE_URL))
            finance_session = await stack.enter_async_context(ClientSession(finance_conn[0], finance_conn[1]))
            await finance_session.initialize()

            # Run tool calls concurrently using asyncio.gather()
            # Note: world_session is used for both news and weather as they are on the same server
            news_task = world_session.call_tool("search_news", arguments={"query": topic})
            weather_task = world_session.call_tool("get_weather", arguments={"city": city})
            fx_task = finance_session.call_tool("get_fx_rate", arguments={"location": city})

            results = await asyncio.gather(news_task, weather_task, fx_task, return_exceptions=True)
            
            # Helper to extract data from CallToolResult or handle exception
            def extract_data(result):
                if isinstance(result, Exception):
                    return {"error": str(result)}
                # The .data payload is usually in result.content[0].text in a JSON string format if returned as dict from tool
                content = result.content[0].text if result.content else "{}"
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    return {"data": content}

            news_data = extract_data(results[0])
            weather_data = extract_data(results[1])
            fx_data = extract_data(results[2])

            # Build a structured signal dictionary
            signal = {
                "topic": topic,
                "city": city,
                "news_context": news_data,
                "weather_context": weather_data,
                "financial_context": fx_data
            }

            # Send the signal to the Scout Agent via the protocol messaging system
            message = {
                "sender": "Contextualist",
                "recipient": "Scout",
                "task_id": task_id,
                "status": "data_gathered",
                "payload": signal
            }
            send_message(message)

            return signal
            
        except Exception as e:
            return {"error": f"Failed to gather context: {str(e)}"}

if __name__ == "__main__":
    mcp.run(transport="sse")
