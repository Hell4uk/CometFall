# CometFall — текстовая MMORPG в Telegram

![Python](https://img.shields.io/badge/python-3.11-blue)
![Aiogram](https://img.shields.io/badge/aiogram-3.22-green)
![Tortoise ORM](https://img.shields.io/badge/tortoise--orm-0.25-orange)
![PostgreSQL](https://img.shields.io/badge/postgres-15-blue)
![License](https://img.shields.io/badge/license-MIT-brightgreen)

---

**CometFall - это современный проект**, который включает в себя **совершенные подходы программирования** и **структуризации**.

Бей врагов, прокачивай меч, собирай дроп, покупай оружия, соревнуйся с другими игроками — и всё это в **Telegram** без **никаких лишних действий**.

[ИГРАТЬ СЕЙЧАС](https://t.me/CometFall_bot)\
тг: @CometFall_bot

---

## Что умеет бот:

---

## Структура проекта:

```
src/
 └─ bot/
     ├─ handlers/      - команды и колбэки
     ├─ keyboards/     - кнопки
     ├─ services/      - сервисы инвентаря, врагов, дропа
     ├─ middlewares/   - проверки, логирование 
     ├─ game/
     │   ├─ logic/     - расчёт урона, брони
     │   ├─ views/     - создание читабельного сообщения
     │   └─ config.py  - конфигурация
     ├─ db/
     │   ├─ models.py  - Users, Items, Enemies
     │   └─ schemas/   - Pydantic-валидация атрибутов
     └─ config.py      - Получения констант из .env, mapping текста

```

---

Наша команда: **TeraCodeFrame**\
тг: @TeraCodeFrame