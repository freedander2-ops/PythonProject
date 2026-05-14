# Agents and Tools

This repository contains a Telegram bot for receiving and managing job applications from contractors.

## Project Overview
- This is a Telegram bot written in [Python/Node].
- It handles user messages, reactions, and applications.
- The bot is designed for receiving job applications for a finisher / contractor.

## Build and Run Commands
- How to install dependencies:
  - `pip install -r requirements.txt` or `npm install`
- How to run the bot:
  - `python bot.py` or `node bot.js`
- How to run in production (if any):
  - `pm2 start bot.js` or systemd service.

## Environment Variables
- List of required env vars:
  - `BOT_TOKEN` — bot token from @BotFather.
  - `ADMIN_IDS` — comma-separated list of admin user IDs.
  - `DATABASE_URL` — connection to database (if used).
- Example file: `.env.example`.

## Code Style
- Use clear function names.
- Handle all exceptions in Telegram handlers.
- Use async/await for Node or asyncio for Python.
- Keep code DRY and follow pep8 if Python.

## Security
- Do not store API tokens in code.
- Handle user input carefully.
- Validate all data before using it.

## Deployment
- Bot runs on a server with systemd or PM2.
- Logs are stored in `/var/log/bot/`.

## How to use Jules
- Let Jules update the bot logic, fix bugs, migrate to new API, add new features.
- Jules should not change environment variables or secrets.
- Always check diffs before merging.
