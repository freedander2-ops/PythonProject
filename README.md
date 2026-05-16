# 🏗 PythonProject: Construction Bot Platform

A modular, capability-oriented Telegram bot platform for managing construction and finishing job applications.

## 🚀 Quick Start
1. **Setup Environment:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Configure:**
   - Copy `.env.example` to `.env`.
   - Set `API_TOKEN` and `ADMIN_ID`.
3. **Run:**
   ```bash
   python run.py
   ```

## 📂 Project Structure
- `run.py`: Main entry point.
- `bot/`: Telegram handlers and keyboards.
- `core/`: Config and system initialization.
- `data/`: Price lists and materials data.
- `services/`: Business logic (Estimates, Materials, Applications).
- `utils/`: Helper functions.

## 🛠 Maintenance
- **Update Prices:** Edit `data/prices.py`.
- **Material Rules:** Edit `data/materials.py`.
- **Logs:** Monitor `bot.log` for events and errors.

Detailed architecture information can be found in [ARCHITECTURE.md](ARCHITECTURE.md).
