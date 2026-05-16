# ARCHITECTURE.md — PythonProject

## Overview
PythonProject is a modular Telegram automation platform designed for maintainability, security, and scalability.

## Core Philosophy
- **Modularity:** Logic is separated into distinct layers (Bot, Core, Services, Utils).
- **Isolation:** Business logic (Services) is decoupled from the communication interface (Bot).
- **Observability:** Structured logging for better debugging and monitoring.
- **Scalability:** The architecture supports the addition of new "capabilities" without affecting the core.

## Directory Structure
- `/bot`: Telegram-specific logic (handlers, keyboards).
- `/core`: System-level configuration and constants.
- `/data`: Static data and price lists.
- `/services`: Domain-specific business logic (Estimate calculation, Application management).
- `/utils`: Common helper functions and shared tools.
- `/run.py`: Application entry point.

## Data Flow
1. **User Interaction:** The user sends a message to the Telegram bot.
2. **Handling:** `bot/handlers.py` receives the event and identifies the intent.
3. **Execution:** The handler delegates the task to the appropriate module in `services/`.
4. **Processing:** Services use data from `data/` and helper functions from `utils/` to compute results.
5. **Response:** The handler receives the result and uses `bot/keyboards.py` to format the final response.

## Security
- API tokens are managed via environment variables (`.env`).
- User input is validated before being processed by services.
- Sensitive information is never hardcoded.
