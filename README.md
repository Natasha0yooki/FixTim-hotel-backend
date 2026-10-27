# Backend API — AI-агент планирования путешествий

**Хакатон:** «О!дин запрос» (Островок)  
**Участник №1:** Backend Developer / Integration Engineer  
**Стек:** Python 3.11+, FastAPI, Pydantic, SQLAlchemy, SQLite (позже PostgreSQL)

Backend принимает сообщения от Frontend, управляет сессиями и состоянием поездки, вызывает AI-агента и возвращает структурированный JSON.  
Логику выбора отелей, Tool Calling и работу с Llama Backend **не реализует**.

---

## 1. Быстрый старт

```bash
# 1. Перейти в корень проекта
cd hotel-ai-agent

# 2. Активировать виртуальное окружение
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac / Linux

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Запустить сервер
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

После запуска:

| Что              | Адрес                              |
|------------------|------------------------------------|
| API              | http://localhost:8000              |
| Swagger (документация) | http://localhost:8000/docs   |
| Health-проверка  | http://localhost:8000/api/v1/health |

---

## 2. Архитектура

```
Frontend (№4)
      │  POST /api/v1/chat
      ▼
FastAPI Backend (№1)          ← единая точка входа
      │  загружает state сессии
      │  вызывает агента
      ▼
Agent Service
      │  сейчас: умная заглушка
      │  позже: AgentOrchestrator (№2)
      ▼
Catalog Gateway (№3)          ← поиск отелей, данные
```

**Зона ответственности Backend:**
- HTTP API и валидация входных данных
- Создание и хранение сессий
- Сохранение полного `updated_state` от агента
- Сериализация ответа для Frontend
- Демо-подтверждение заказа (checkout)

**Backend НЕ делает:**
- Парсинг естественного языка
- Вызовы Ollama / Llama
- Tool Calling
- Поиск по каталогу и SQL/RAG

---

## 3. Реализованные эндпоинты

| Метод | URL                                 | Описание                                      | Статус |
|-------|-------------------------------------|-----------------------------------------------|--------|
| POST  | `/api/v1/chat`                      | Главный эндпоинт: сообщение → ответ агента    | ✅     |
| GET   | `/api/v1/sessions/{session_id}/messages` | История сообщений сессии                 | ✅     |
| GET   | `/api/v1/hotels/{hotel_id}`         | Детали отеля (пока заглушка)                  | ✅     |
| POST  | `/api/v1/checkout/confirm`          | Демо-подтверждение заказа                     | ✅     |
| GET   | `/api/v1/health`                    | Проверка состояния сервиса                    | ✅     |
| GET   | `/api/v1/destinations`              | Список направлений                            | ⏳     |
| GET   | `/api/v1/trips/{session_id}`        | Текущий план поездки                          | ⏳     |

---

## 4. Контракт POST /api/v1/chat

### Запрос

```json
{
  "session_id": "uuid-или-null",
  "message": "Хочу на море на 5 дней"
}
```

- Если `session_id` не передан или сессия не найдена — создаётся новая.
- `message` — одно новое сообщение пользователя.

### Ответ

```json
{
  "session_id": "c241b688-6c9c-4627-ab8e-fcd82d2c6520",
  "status": "results",
  "reply": "Нашла несколько вариантов у моря. Выберите направление:",
  "stage": "destinations",
  "destinations": [
    {
      "id": "sochi",
      "name": "Сочи",
      "reason": "Тёплое море, горы рядом",
      "price_from": 45000,
      "currency": "RUB"
    }
  ],
  "hotels": [],
  "itinerary": null,
  "cart": null,
  "warnings": [
    { "level": "info", "text": "Данные синтетические (демо-режим)" }
  ],
  "is_demo": true,
  "state": { ... }
}
```

### Возможные значения `status`

| status          | Значение                                      |
|-----------------|-----------------------------------------------|
| `clarification` | Агент просит уточнение                        |
| `results`       | Есть полезный ответ / результаты              |
| `no_results`    | Подходящих вариантов не найдено               |
| `error`         | Произошла ошибка (пользовательское сообщение) |

### Возможные значения `stage` (для Frontend)

- `inspiration` — начальный этап / уточнение
- `destinations` — показ направлений
- `hotels` — показ отелей
- `itinerary` — маршрут
- `checkout` — корзина и оформление

---

## 5. Как работает состояние (state)

1. При первом сообщении Backend передаёт агенту `state = {}`.
2. Агент возвращает `updated_state` — полный словарь с параметрами поездки.
3. Backend **сохраняет его целиком** в сессии (SQLite).
4. При следующем сообщении Backend достаёт сохранённый state и снова передаёт агенту.

**Важно:** Backend не редактирует и не фильтрует поля внутри `updated_state`.  
Именно так агент сохраняет город, даты, выбранные отели, `last_hotel_ids` и т.д.

---

## 6. Текущая заглушка агента

Файл: `backend/app/services/agent_service.py`

Пока настоящего агента нет, используется умная заглушка.  
Она смотрит на ключевые слова и возвращает разные стадии:

| Ключевые слова пользователя          | stage         | Что возвращает          |
|--------------------------------------|---------------|-------------------------|
| море, сочи, отдых, куда, направление | `destinations`| Список направлений      |
| отель, отели, выбираю, покажи        | `hotels`      | Список отелей           |
| маршрут, план, таймлайн              | `itinerary`   | Таймлайн маршрута       |
| корзина, оформить, бронь, checkout   | `checkout`    | Корзина                 |
| всё остальное                        | `inspiration` | Уточняющий вопрос       |

Заглушка полностью совместима с контрактом настоящего агента (`updated_state`, `warnings: list[str]` и т.д.).

---

## 7. Подключение настоящего агента

Когда появятся пакеты `backend.app.agent` и `backend.app.catalog`, нужно заменить только заглушку.

### Создание агента (один раз при старте)

```python
from backend.app.agent import AgentOrchestrator
from backend.app.catalog.service import get_catalog_gateway

catalog = get_catalog_gateway()
agent = AgentOrchestrator(catalog=catalog)
```

### Тело handle_message

```python
async def handle_message(
    session_id: str,
    message: str,
    state: dict,
) -> AgentResponse:
    result = await agent.handle_message(
        session_id=session_id,
        message=message,
        state=state or {},
    )
    return result
```

Всё остальное (сохранение `updated_state`, формирование HTTP-ответа, маппинг `warnings`) уже реализовано и менять не нужно.

---

## 8. Структура проекта

```
hotel-ai-agent/
├── .env / .env.example
├── requirements.txt
├── hotel_agent.db                 # SQLite (создаётся автоматически)
│
└── backend/app/
    ├── main.py                    # FastAPI app, CORS, подключение роутеров
    │
    ├── core/
    │   ├── config.py              # настройки из .env
    │   └── errors.py              # единый формат ошибок
    │
    ├── api/                       # HTTP-слой
    │   ├── chat.py                # POST /api/v1/chat
    │   ├── sessions.py            # история сообщений
    │   ├── hotels.py              # детали отеля
    │   └── checkout.py            # демо-подтверждение
    │
    ├── contracts/                 # Pydantic-модели запросов/ответов
    │
    ├── sessions/                  # работа с сессиями
    │   ├── models.py              # таблицы Session, Message
    │   ├── repository.py          # доступ к БД
    │   └── service.py             # бизнес-логика сессий
    │
    └── services/
        └── agent_service.py       # заглушка + точка подключения агента
```

---

## 9. Checkout (демо-бронирование)

```
POST /api/v1/checkout/confirm
Body: { "session_id": "..." }
```

- Никакой реальной оплаты нет.
- В `state` сессии ставится флаг `demo_booked = True`.
- Возвращается статус успешного демо-подтверждения.

---

## 10. Что осталось сделать

| Задача                                      | Приоритет | Комментарий                              |
|---------------------------------------------|-----------|------------------------------------------|
| Подключить AgentOrchestrator                | Высокий   | Ждём код от участника №2                 |
| Подключить реальный CatalogGateway          | Высокий   | Ждём код от участника №3                 |
| GET /api/v1/destinations                    | Средний   | Можно отдать данные из state             |
| GET /api/v1/trips/{session_id}              | Средний   | Можно отдать itinerary + cart из state   |
| Docker                                      | Низкий    | После стабилизации API                   |
| PostgreSQL вместо SQLite                    | Низкий    | После хакатона / при росте нагрузки      |
| Более строгое логирование                   | Низкий    | По необходимости                         |

---

## 11. Полезные команды для проверки

```bash
# Health
curl http://localhost:8000/api/v1/health

# Пример чата
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"Хочу на море\"}"

# Swagger
http://localhost:8000/docs
```

---
