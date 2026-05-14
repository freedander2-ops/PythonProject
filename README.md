# 👷 Telegram Бот для строителей и отделочников

Этот бот предназначен для автоматизации приема заявок на отделочные работы и предоставления пользователям удобных инструментов для расчета сметы и материалов.

## ✨ Особенности
- **Расчет сметы:** Узнайте примерную стоимость работ в несколько кликов.
- **Калькулятор материалов:** Рассчитайте количество плитки, кирпича или блоков с учетом запаса.
- **Подача заявки:** Оформите заявку с описанием задачи, сроками и фотографиями объекта.
- **Админ-уведомления:** Мгновенное получение заявок администратором.

---

## 🚀 Быстрый старт

### 1. Подготовка окружения
Убедитесь, что у вас установлен Python 3.8+.

```bash
# Установка зависимостей
pip install -r requirements.txt
```

### 2. Настройка конфигурации
Создайте файл `.env` в корневом каталоге на основе `.env.example`:

```env
API_TOKEN=ваш_токен_от_BotFather
ADMIN_ID=ваш_id_в_telegram
```

### 3. Запуск бота
```bash
python main.py
```

---

## 📂 Структура проекта
- `main.py` — Основной файл с обработчиками сообщений Telegram.
- `src/`
  - `config.py` — Загрузка настроек и константы.
  - `data.py` — Прайс-листы и параметры материалов.
  - `keyboards.py` — Генерация всех меню (Reply и Inline).
  - `utils.py` — Вспомогательные функции (защита от спама, работа с файлами).
- `requests/` — Папка для временного хранения фотографий.

---

## 🛠 Обслуживание
- **Обновление цен:** Все цены находятся в `src/data.py`.
- **Логи:** Ошибки и важные события записываются в `bot.log`.
- **Очистка:** Бот автоматически удаляет временные фотографии старше 24 часов.

---

# 👷 Construction & Finishing Telegram Bot

This bot is designed to automate the process of receiving job applications for finishing works and provide users with convenient tools for estimating costs and materials.

## ✨ Features
- **Estimate Calculation:** Get an approximate cost of work in a few clicks.
- **Material Calculator:** Calculate the quantity of tiles, bricks, or blocks, including waste.
- **Application Submission:** Submit an application with a description, deadlines, and photos of the site.
- **Admin Notifications:** Instant delivery of applications to the administrator.

---

## 🚀 Quick Start

### 1. Environment Setup
Ensure you have Python 3.8+ installed.

```bash
# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration
Create a `.env` file in the root directory based on `.env.example`:

```env
API_TOKEN=your_token_from_BotFather
ADMIN_ID=your_telegram_id
```

### 3. Run the Bot
```bash
python main.py
```
