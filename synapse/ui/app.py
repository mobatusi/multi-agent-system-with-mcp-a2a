import streamlit as st
import asyncio
import json
import os
import re
from openai import OpenAI
from dotenv import load_dotenv
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client

# Build Streamlit Interface to Trigger Agents

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Upstream Agent URLs
SCOUT_AGENT_URL = "http://127.0.0.1:8004/sse"
PUBLISHER_AGENT_URL = "http://127.0.0.1:8005/sse"

client = OpenAI(api_key=api_key)

def get_location_context(news_text: str) -> dict:
    """
    Extracts country and capital from a text string using an LLM.
    """
    prompt = f"""
    Given the news text below, identify the primary country it is about.
    Return only a JSON object with the keys 'country' and 'capital'.
    If no country is mentioned, return US and its capital for both.

    Text: "{news_text}"
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={ "type": "json_object" }
    )

    return json.loads(response.choices[0].message.content)

async def run_scout(topic: str, city: str):
    """
    Call the Scout Agent to orchestrate data gathering and aggregation.
    """
    async with sse_client(SCOUT_AGENT_URL) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.call_tool("scout", arguments={"topic": topic, "city": city})
            return json.loads(result.content[0].text)

async def run_publisher(payload: dict):
    """
    Call the Publisher Agent to generate the final article.
    """
    async with sse_client(PUBLISHER_AGENT_URL) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.call_tool("publish_brief", arguments={"payload": payload})
            return json.loads(result.content[0].text)

# Streamlit UI Components
st.set_page_config(page_title="Synapse Daily Brief", page_icon="📝", layout="wide")
st.title("📝 Synapse: Multi-Agent Daily Brief")
st.write("Generate a professional journalistic report based on real-time news, weather, and financial data.")

topic = st.text_input("Enter a topic (e.g., 'Tech stocks', 'Climate change', 'Oil prices')", placeholder="AI Innovation")

if st.button("Generate Report"):
    if not topic:
        st.warning("Please enter a topic.")
    else:
        with st.spinner("Generating report... this involves multiple agents coordinating."):
            try:
                # 1. Get Location Context
                location = get_location_context(topic)
                city = location.get("capital", "Washington D.C.")
                
                # 2. Run Scout Agent (Orchestration)
                scout_data = asyncio.run(run_scout(topic, city))
                
                # 3. Run Publisher Agent (Content Generation)
                final_results = asyncio.run(run_publisher(scout_data))
                
                # 4. Success State
                st.success("Report Generated!")
                st.markdown("---")

                # Layout: Two columns for Image and Header info
                col1, col2 = st.columns([1, 2])
                
                original_payload = final_results.get("original_payload", {})
                media_data = original_payload.get("media", {})
                images = media_data.get("images", [])
                
                with col1:
                    if images:
                        st.image(images[0].get("src"), caption=images[0].get("alt", "Topic Image"))
                    else:
                        st.info("No images found for this topic.")
                
                with col2:
                    st.header(f"Topic: {topic}")
                    st.subheader(f"Location Context: {city}")
                    st.write(f"Generated at: {java_time := ''}") # Placeholder for time if needed
                
                st.markdown("---")
                
                # Main Article in an Expander
                article_content = final_results.get("article", "No article content available.")
                
                with st.expander("📖 Read Full Daily Brief", expanded=True):
                    # Attempt to split by sections if headers exist (Common LLM pattern uses # or **Section**)
                    # For now, we'll use a split regex for common headers
                    sections = re.split(r'\n(?=#{1,3} |\*\*.*?\*\*)', article_content)
                    
                    if len(sections) > 1:
                        for section in sections:
                            st.markdown(section.strip())
                    else:
                        st.markdown(article_content)

                # Secondary Sections for Technical Data
                st.markdown("### 🛠 Agent Signals & Raw Data")
                tab1, tab2 = st.tabs(["Signal Payload", "Raw Response"])
                
                with tab1:
                    st.json(original_payload)
                
                with tab2:
                    st.json(final_results)
                    
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.exception(e)
