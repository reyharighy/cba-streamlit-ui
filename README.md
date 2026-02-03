<div id="top">

<div align="center">

# CONVERSATIONAL BUSINESS ANALYTICS

<em>Interactive Streamlit Interface for Agentic Business Analytics</em>

<em>Built with:</em>

<img src="https://img.shields.io/badge/Python-3776AB.svg?style=flat&logo=Python&logoColor=white">
<img src="https://img.shields.io/badge/Streamlit-FF4B4B.svg?style=flat&logo=Streamlit&logoColor=white">
<img src="https://img.shields.io/badge/Docker-2496ED.svg?style=flat&logo=Docker&logoColor=white">

</div>

---

## Overview

This repository contains the Streamlit-based user interface for Conversational Business Analytics (CBA).

The UI acts as a thin, reactive client over a remote agentic FastAPI service, responsible for:

- capturing user questions,
- streaming agent reasoning and execution updates in real time,
- rendering intermediate and final outputs,
- and exposing conversational history to the user.

All analytical reasoning, planning, execution, and memory management live in the backend agent service.

Please check this repo: [cba-agentic-ai/tree/agent-service-fastapi](https://github.com/reyharighy/cba-agentic-ai/tree/agent-service-fastapi).

---

## Project Status

⚠️ **Active Development**

The UI is evolving alongside the agent architecture, with current focus on:

- reliable Server-Sent Events (SSE) streaming,
- deterministic rendering of partial agent updates,
- clean separation between updates, completion, and error states,
- and graceful UI recovery when the agent graph fails mid-execution.

UI behavior may change as the backend streaming protocol evolves.

---

## Architecture Role

### Client–Agent Separation

This UI follows a strict client–server boundary:

### 1. Streamlit UI

- Input capture
- Event stream consumption
- Visualization & presentation
- Session-local UI state

### 2. FastAPI Agent Service

- Intent comprehension
- Planning
- Tool execution
- Observation loops
- Memory persistence

No agent reasoning is duplicated here.

---

## Streaming Model: Event-Driven UI

The UI consumes agent output via Server-Sent Events (SSE).

Each event is a structured JSON payload wrapped in an SSE frame:

```sh
data: { "type": "update", "data": {...} }

data: { "type": "complete" }

data: { "type": "error", "message": "..." }
```

### Why SSE?

- deterministic ordering,
- low overhead,
- native browser & Streamlit compatibility,
- well-suited for long-running, incremental reasoning.

The UI renders output incrementally, not after full completion.

## Getting Started

### Prerequisites

You will need:

- **Docker**
- **Docker Compose**
- **Git**

No local Python installation is required if using Docker.

### Environment Setup

This project uses environment variables for configuration.

1. Copy the example file:

    ```sh
    cp .env.example .env
    ```

2. Configure the agent endpoint:

    ```sh
    AGENT_API_BASE_URL=http://agent-api:8000
    ```

### Installation

Clone the repository:

```sh
git clone https://github.com/reyharighy/cba-streamlit-ui.git

cd cba-streamlit-ui
```

### Running the UI

```sh
docker compose up --build
```

Then open:

```sh
http://localhost:8501
```

## Docker Networking Notes

This UI is designed to run against an externally hosted FastAPI endpoint.

When using Docker Compose with an external network:

```yaml
networks:
  net-system:
    external: true
```

The agent service must already be attached to that network.

## Design Principles

- UI logic must remain stateless with respect to reasoning
- Rendering must tolerate partial, delayed, or failed agent output
- Every streamed message must be typed
- Completion and failure are explicit states, not assumptions
- If the agent is confused, the UI should not pretend otherwise

## Notes for Contributors

- This is not a “smart UI”
- Do not move reasoning into Streamlit
- If something feels implicit, make it an event type
- UI resilience matters more than UI cleverness
- Broken reasoning should be visible, not hidden

<br>

---

<div align="left"><a href="#top">⬆ Return</a></div>

---
