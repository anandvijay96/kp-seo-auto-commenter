# Phase 1 Execution Plan: MVP Foundation

> **Document Purpose**: This document provides a detailed engineering plan for the successful execution of Phase 1, as outlined in the Master PRD. It translates the strategic objective into concrete tasks and deliverables.

---

## 1. Phase 1 Objective

To build the core data ingestion and content generation capabilities of the platform. This includes a robust web crawler to discover target blogs and a foundational AI service to generate contextually relevant comments. This phase lays the groundwork for all subsequent intelligence and submission features.

*   **Timeline**: Month 1
*   **PRD Success Metrics**:
    *   Crawler capacity: ≥ 100 blogs/hour.
    *   Comment validity: ≥ 80% of generated comments are contextually valid and pass a basic quality check.

---

## 2. Key Deliverables & Task Breakdown

### Deliverable 1: Discovery Crawler Service

*   **Description**: A microservice responsible for discovering and scraping content from target blogs.
*   **Tasks**:
    1.  **Scaffolding & Environment Setup**:
        *   [ ] Initialize a new FastAPI service directory (`app/services/crawler`).
        *   [ ] Configure Playwright with necessary browser dependencies within a dedicated Docker container.
        *   [ ] Establish and verify database connectivity to the PostgreSQL instance.
    2.  **Data Modeling & Migrations**:
        *   [ ] Implement SQLAlchemy models for `blogs` and `blog_posts` tables as per the PRD schema.
        *   [ ] Generate and apply Alembic migration scripts for the initial schema.
    3.  **Crawler Logic**:
        *   [ ] Develop logic to ingest a list of seed URLs from a configuration file or database table.
        *   [ ] Implement the core Playwright script to navigate, extract post links, and scrape article content.
        *   [ ] Design a basic queuing mechanism using RabbitMQ to manage crawling jobs asynchronously.
    4.  **Data Persistence**:
        *   [ ] Create a repository pattern (`app/core/repositories`) to handle saving scraped `blogs` and `blog_posts` data to PostgreSQL.
        *   [ ] Implement logic to avoid duplicate post entries.

### Deliverable 2: Basic Gemini Comment Generator Service

*   **Description**: A microservice that uses Google Gemini to generate comments based on scraped blog content.
*   **Tasks**:
    1.  **Service Scaffolding**:
        *   [ ] Initialize a new FastAPI service directory (`app/services/generator`).
        *   [ ] Implement secure loading of the Google Gemini API key from AWS Secrets Manager (or `.env` for local).
    2.  **Prompt Engineering (v1)**:
        *   [ ] Implement the initial `analysis_prompt` and `generation_prompt` templates as defined in the master PRD.
        *   [ ] Create Pydantic models to structure prompt inputs and validate expected outputs from the AI.
    3.  **Core Generation Logic**:
        *   [ ] Implement a function that takes `blog_post` content, constructs the appropriate prompt, and calls the Google Gemini API.
        *   [ ] Add robust error handling for API failures, timeouts, or malformed responses.
    4.  **API Endpoint & Persistence**:
        *   [ ] Expose a RESTful endpoint (e.g., `POST /api/v1/generate_comment`) that accepts a `post_id`.
        *   [ ] Implement the logic to fetch post content, trigger the generation workflow, and save the result to the `comments` table with a `pending_review` status.

---

## 3. Definition of Done for Phase 1

*   [ ] All code is peer-reviewed, formatted, and merged into the `develop` branch.
*   [ ] Unit tests achieve >80% code coverage for all new services and repositories.
*   [ ] The crawler can successfully process a seed list of 20 sample blogs and persist the data correctly.
*   [ ] The generator API successfully creates valid comments for at least 15 of the 20 scraped posts.
*   [ ] A live demonstration of the end-to-end flow (Crawl → Generate → View in DB) is successfully presented to stakeholders.
*   [ ] All infrastructure changes are codified in Docker and `docker-compose.yml`.
