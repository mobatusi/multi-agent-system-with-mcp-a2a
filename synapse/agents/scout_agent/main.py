import asyncio
import json
import time
from contextlib import AsyncExitStack
from mcp.server.fastmcp import FastMCP
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client
from synapse.protocol.post_office import send_message, read_messages, clear_messages

# Task 8: Build Scout Agent to Aggregate Signals

# Define upstream service URLs
CONTEXTUALIST_URL = "http://127.0.0.1:8000/sse"
MEDIA_ENGINE_URL = "http://127.0.0.1:8003/sse"

mcp = FastMCP("Scout Agent", port=8004)

async def _wait_for_response(task_id: str, timeout: int = 30) -> dict:
    """
    Polls the post office for a message matching the task_id.
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        messages = read_messages()
        for msg in messages:
            if msg.get("task_id") == task_id and msg.get("status") == "data_gathered":
                return msg.get("payload", {})
        await asyncio.sleep(1)
    
    raise TimeoutError(f"Timed out waiting for response with task_id: {task_id}")

@mcp.tool()
async def scout(topic: str, city: str, task_id: str = "scout_task") -> dict:
    """
    Coordinate contextualization and media gathering for a topic.
    """
    # Clear previously stored messages to avoid stale data
    clear_messages()
    
    async with AsyncExitStack() as stack:
        try:
            # Connect to Contextualist Agent
            ctx_conn = await stack.enter_async_context(sse_client(CONTEXTUALIST_URL))
            ctx_session = await stack.enter_async_context(ClientSession(ctx_conn[0], ctx_conn[1]))
            await ctx_session.initialize()
            
            # Connect to Media Engine Agent
            media_conn = await stack.enter_async_context(sse_client(MEDIA_ENGINE_URL))
            media_session = await stack.enter_async_context(ClientSession(media_conn[0], media_conn[1]))
            await media_session.initialize()

            # 1. Trigger Contextualization
            print(f"Triggering contextualization for topic: {topic} in {city}...")
            await ctx_session.call_tool("contextualize", arguments={"topic": topic, "city": city, "task_id": task_id})
            
            # 2. Poll for the contextual signal from the post office
            print("Waiting for contextualization signal...")
            contextual_data = await _wait_for_response(task_id)
            
            # 3. Call Media Engine for images
            print(f"Searching for images for topic: {topic}...")
            media_result = await media_session.call_tool("search_images", arguments={"query": topic, "count": 2})
            
            # Extract media data
            media_content = media_result.content[0].text if media_result.content else "{}"
            try:
                media_data = json.loads(media_content)
            except json.JSONDecodeError:
                media_data = {"data": media_content}

            # Combine everything into a single final signal
            final_signal = {
                "topic": topic,
                "city": city,
                "context": contextual_data,
                "media": media_data
            }

            # Send the aggregated signal to the Publisher agent
            publisher_message = {
                "sender": "Scout",
                "recipient": "Publisher",
                "task_id": task_id,
                "status": "aggregation_complete",
                "payload": final_signal
            }
            send_message(publisher_message)

            return final_signal
            
        except Exception as e:
            return {"error": f"Scout aggregation failed: {str(e)}"}

if __name__ == "__main__":
    mcp.run(transport="sse")
