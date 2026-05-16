# Agents and Tools - PythonProject

## Project Overview
This is a high-quality, modular Python platform for Telegram-based automation.

## Rules for Agents
- **Preserve Architecture:** Follow the `/bot`, `/core`, `/services`, `/utils` structure.
- **Lightweight Handlers:** Keep UI logic in `bot/` and business logic in `services/`.
- **Russian Comments:** Maintain comments in Russian for readability and context.
- **Logging:** Use the logger from `core.config` for consistency.

## Capability Extension
To add a new feature (e.g., OSINT, AI), create a new service in `services/` and a corresponding handler in `bot/`.

## Deployment
- Use systemd or PM2 to manage `run.py`.
- Ensure `.env` is properly set up on the server.
