# Future Roadmap - Synapse Multi-Agent System

This document outlines the next steps for enhancing the Synapse Multi-Agent System beyond the initial implementation.

## Phase 1: Automation & Scheduling

### Automated Daily Reports
- **Goal**: Trigger the agentic pipeline automatically at a set time every day.
- **Approach**: 
    - Implement a standalone Python script `synapse/scripts/auto_brief.py` that utilizes the current Agent messaging protocol.
    - Use `apscheduler` or a simple system `cron` job to execute the script daily.
    - Resulting briefs can be e-mailed or pushed to a notification service (e.g., Slack/Discord).

## Phase 2: Signal Enrichment

### Multi-Location Support
- **Goal**: Generate briefs for multiple cities in a single run.
- **Approach**: 
    - Update the `contextualize` tool to accept a list of cities.
    - Modify the Scout Agent to iterate through location contexts.

### Expanded Data Sources
- **Goal**: Incorporate social media trending topics and deeper financial news.
- **Approach**:
    - [NEW] MCP Server: `social-monitor` (connecting to Reddit or Twitter API).
    - [NEW] MCP Server: `financial-deep-dive` (using Bloomberg or Yahoo Finance endpoints).

## Phase 3: UI/UX & Intelligence

### Dynamic UI Widgets
- **Goal**: Integrate Plotly/Altair charts for currency trends and weather forecasts.
- **Approach**: 
    - Update the `app.py` to parse structured numeric data and render interactive visualizations.

### LLM Multi-Model Experimentation
- **Goal**: Compare outputs from different models (Claude 3.5, Gemini 1.5 Pro).
- **Approach**: 
    - Implement a "Model Switcher" in the UI sidebar to toggle backend generation.
    - Refine prompt templates for "Long-form", "Summary", and "Executive" styles.

## Phase 4: Production Readiness

### Robust Error Handling & Retries
- **Goal**: Handle API rate limits and network failures gracefully.
- **Approach**: 
    - Use `tenacity` for retrying failed tool calls.
    - Implement a circuit breaker pattern for external API dependencies.
