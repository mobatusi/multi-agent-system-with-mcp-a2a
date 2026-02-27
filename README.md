# Build a Multi Agent System with MCP and A2A

## Overview
This project builds an AI-powered news brief generator using Model Context Protocol (MCP) and Agent-to-Agent (A2A) orchestration. It is a multi-agent system that collects real-time news, weather, finance, and media data. It aggregates these signals using explicit message passing between specialized agents and uses a Large Language Model (LLM) to generate a daily brief. The final output is delivered via an interactive Streamlit application.

Based on the Educative.io project: [Build a Multi Agent System with MCP and A2A](https://www.educative.io/projects/build-multi-agent-system-with-mcp-a2a).

## Features
- **MCP Infrastructure**: Custom MCP servers that expose tools over HTTP for weather, news, finance, and media data sources.
- **A2A Orchestration**: Coordinating multiple specialized agents (Scout, Contextualist, Publisher) using FastMCP and message passing.
- **Third-party API Integration**: Securely fetching contextual real-world data from multiple external APIs.
- **AI-driven Content Generation**: Using LLMs to aggregate data, parse responses, and generate structured, context-aware daily articles.
- **Interactive UI**: A Streamlit interface to trigger the agents, monitor agent execution, and display the generated daily briefs.
- **Data Validation**: Validating and normalizing external API outputs for robust downstream agent usage.

## Technologies
- **Language**: Python 3
- **AI & LLM**: Generative AI, Large Language Models (LLMs), OpenAI API
- **Agent Orchestration & Protocol**: Model Context Protocol (MCP), FastMCP
- **Frontend**: Streamlit
- **External APIs**: OpenWeather, Pexels, NewsAPI, ExchangeRate API

## Project Structure
```text
multi-agent-system-with-mcp-a2a/
├── synapse/
│   ├── agents/          # Specialized agents (Scout, Contextualist, Publisher)
│   ├── mcp-servers/     # MCP servers (World Data, Weather, Finance, Media Engine)
│   ├── protocol/        # Agent messaging protocols
│   ├── ui/              # Streamlit interface components
│   ├── agent.py         # Agent definitions and execution
│   ├── server.py        # Core MCP server logic
│   └── env.txt          # Environment variables template
├── README.md            # Project documentation
├── LICENSE              
├── .gitignore           
```

## Quick Start & Usage

### 1. Pre-requisites
Ensure you have Python 3 installed. You will need API keys for the following services:
- **OpenAI**: For LLM generation.
- **OpenWeather**: For fetching live weather data.
- **Pexels**: For fetching high-quality topic-related images.
- **NewsAPI**: For fetching news headlines.
- **ExchangeRate API**: For retrieving currency exchange rates.

### 2. Environment Setup
1. Clone the repository and navigate to the project root.
2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Navigate to the `synapse/` directory.
4. Duplicate `env copy.txt` and name it `env.txt`.
5. Add your API keys to the `env.txt` file!

### 3. Running the System
To run the full pipeline, start the components in separate terminals:

1. **World Data Server (News/Weather)**:
   ```bash
   python synapse/mcp-servers/world-data/server.py
   ```
2. **Finance Monitor**:
   ```bash
   python synapse/mcp-servers/finance-monitor/server.py
   ```
3. **Media Engine**:
   ```bash
   python synapse/mcp-servers/media-engine/server.py
   ```
4. **Contextualist Agent**:
   ```bash
   python synapse/agents/contextualist_agent/main.py
   ```
5. **Scout Agent**:
   ```bash
   python synapse/agents/scout_agent/main.py
   ```
6. **Publisher Agent**:
   ```bash
   python synapse/agents/publisher_agent/main.py
   ```
7. **Streamlit UI**:
   ```bash
   streamlit run synapse/ui/app.py
   ```

## Future Enhancements
We are moving towards a more robust production-ready system. Planned updates include:
- **Scheduling**: Automated daily reports via cron/task schedulers.
- **Rich Media**: Integrated charts and tables for financial/weather data.
- **Multi-Model Support**: Ability to toggle between GPT-4, Claude, and Gemini.
- **Expanded Intelligence**: Additional signals from social media and deep financial news.

## Implementation Steps (Tasks)

**1. Introduction**
- Task 0: Get Started
- Task 1: Get API Keys (OpenAI, OpenWeather, Pexels, NewsAPI, ExchangeRate API). Store them in `synapse/.env`.

**2. MCP Infrastructure**
- Task 2: Implement World Data MCP Server
- Task 3: Implement Weather MCP Tool and Run the Server
- Task 4: Implement Finance MCP Server
- Task 5: Implement Media Engine MCP Server

**3. Agent-to-Agent Orchestration**
- Task 6: Set Up Agent Messaging Protocol
- Task 7: Build Contextualist Agent to Fetch Contextual Data
- Task 8: Build Scout Agent to Aggregate Signals
- Task 9: Build Publisher Agent to Generate Articles

**4. User Interface**
- Task 10: Build Streamlit Interface to Trigger Agents
- Task 11: Improve Article Readability in the UI
