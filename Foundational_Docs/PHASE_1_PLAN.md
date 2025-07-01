# Phase 1 Execution Plan: The Autonomous Commenting Agent (MVP)

This document outlines the deliverables for building the Minimum Viable Product (MVP) of the SEO Commenting Agent. The architecture is centered around an autonomous agent that uses a set of tools to achieve a high-level goal.

---

## 1. MVP Goal

To build a foundational agent capable of executing a mission from start to finish: **Given a topic, find a relevant blog post, analyze its content, and draft a high-quality, relevant comment.**

---

## 2. Core Architecture

The system will be built around three core concepts:

*   **Agent Core**: The reasoning loop (powered by LangChain and Google Gemini) that decides what to do next.
*   **Toolbelt**: A collection of Python functions (Tools) that the agent can choose to execute. Examples: `search_the_web`, `scrape_a_webpage`, `draft_a_comment`.
*   **Memory**: A mechanism for the agent to persist its findings and the results of its actions, using our PostgreSQL database.

---

## 3. Phase 1 Deliverables

### Deliverable 1: Agent & Tooling Foundation

*   **Description**: Create the foundational scaffolding for the agent and its tools.
*   **Tasks**:
    *   [ ] Create a new `app/agents` directory for all agent-related logic.
    *   [ ] Implement the main agent executor using LangChain, configured with the Gemini model.
    *   [ ] Define a base `Tool` class or interface to ensure all tools have a consistent structure.
    *   [ ] Create a `toolbelt.py` file to register and hold all available tools.

### Deliverable 2: Essential Tool Development

*   **Description**: Build the initial set of tools the agent needs to accomplish its MVP goal.
*   **Tasks**:
    *   [ ] **`web_search_tool`**: Implement a tool that uses the DuckDuckGo Search API to find relevant blog posts for a given topic.
    *   [ ] **`scrape_website_tool`**: Implement a tool that uses Playwright to scrape the full text content of a given URL.
    *   [ ] **`summarize_content_tool`**: Implement a tool that takes a large piece of text (scraped content) and uses Gemini to extract the key arguments and tone.
    *   [ ] **`draft_comment_tool`**: Implement a tool that takes the content summary and a goal, and uses Gemini to write a high-quality draft comment.

### Deliverable 3: API & Persistence

*   **Description**: Expose the agent via an API endpoint and ensure its work is saved.
*   **Tasks**:
    *   [ ] Create a new `Mission` model in `models.py` to track agent runs (e.g., goal, status, logs, results).
    *   [ ] Create a new API endpoint `POST /api/v1/missions` that accepts a goal (e.g., `{"goal": "Write a comment about Python decorators"}`).
    *   [ ] This endpoint will initialize the agent and start its execution loop in the background.
    *   [ ] Implement logic to save the agent's thoughts, actions, and final result to the `Mission` and `Comment` tables.

---

## 4. Definition of Done for Phase 1

*   [ ] All code is peer-reviewed, formatted, and merged into the `develop` branch.
*   [ ] Unit tests achieve >80% code coverage for all new tools and agent components.
*   [ ] The agent can successfully complete a full mission when triggered by the API endpoint.
    *   Example: `POST /api/v1/missions` with goal `"Find a recent blog post about FastAPI and write a thoughtful comment."`
*   [ ] The agent's final drafted comment is successfully saved to the `comments` table with a `pending_review` status.
