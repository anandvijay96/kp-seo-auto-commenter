# KloudPortal SEO Blog Commenting Automation

This repository contains the source code for the KloudPortal SEO Blog Commenting Automation platform.

## Overview

The goal of this project is to create an intelligent system that can automatically discover relevant blog posts, generate insightful comments using AI, and post them to build backlinks, increase brand awareness, and generate leads.

For detailed architecture, planning, and requirements, please see the documents in the `Foundational_Docs/` directory.

## Database Setup

1.  **Create an environment file** by copying the example:
    ```bash
    cp .env.example .env
    ```
2.  **Edit the `.env` file** and add your `GEMINI_API_KEY`.
3.  **Initialize the database** by running the following command from the root directory:
    ```bash
    python init_db.py
    ```

## Getting Started

Follow the instructions in `Foundational_Docs/PRD.md` to set up the local development environment.
