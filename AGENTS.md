# Agents and Tools

This repository contains a modular Telegram bot for receiving and managing job applications from contractors.

## Project Overview
- **Core:** Python bot using `pyTelegramBotAPI`.
- **Structure:** Modularized logic in the `src/` directory.
- **Purpose:** Handling user applications for finishing and construction works.

## Build and Run Commands
- **Install dependencies:** `pip install -r requirements.txt`
- **Run the bot:** `python main.py`
- **Setup:** Copy `.env.example` to `.env` and fill in your credentials.

## Directory Structure
- `main.py`: Entry point and message handlers.
- `src/config.py`: Environment variable loading and global constants.
- `src/data.py`: Price lists and material data.
- `src/keyboards.py`: Telegram markup generation.
- `src/utils.py`: Spam protection, session management, and file utilities.

## Maintenance
- **Prices & Materials:** Update `src/data.py` to change price lists or calculator parameters.
- **UI/Texts:** Modify `main.py` for message texts and `src/keyboards.py` for buttons.
- **Logs:** Check `bot.log` for runtime issues.

## Guidelines for Jules
- Maintain the modular structure.
- Always add Russian comments to explain the logic of new code.
- Ensure all new features are verified with smoke tests.
- Do not commit actual secrets to `.env`.
