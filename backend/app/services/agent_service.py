"""
Сейчас здесь умная заглушка, которая имитирует разные стадии,
чтобы Frontend мог работать.

Когда появится настоящий агент (backend.app.agent),
нужно будет раскомментировать блок внизу и убрать заглушку.
"""

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


# ============================================================
# Контракт ответа агента
# ============================================================

class AgentResponse(BaseModel):
    """То, что возвращает AI-агент (и наша заглушка тоже)."""

    status: Literal["clarification", "results", "no_results", "error"]
    reply: str
    hotels: List[Dict[str, Any]] = Field(default_factory=list)

    # Важно: поле называется updated_state
    updated_state: Dict[str, Any] = Field(default_factory=dict)

    stage: Optional[str] = None
    destinations: List[Dict[str, Any]] = Field(default_factory=list)
    transport_options: List[Dict[str, Any]] = Field(default_factory=list)
    itinerary: Optional[Dict[str, Any]] = None
    cart: Optional[Dict[str, Any]] = None
    warnings: List[str] = Field(default_factory=list)  # list[str], не dict


# ============================================================
# Заглушка (пока нет настоящего агента)
# ============================================================

async def handle_message(
    session_id: str,
    message: str,
    state: Dict[str, Any],
) -> AgentResponse:
    """
    Интерфейс Backend → Agent.

    Сейчас — умная заглушка.
    Позже здесь будет вызов настоящего AgentOrchestrator.
    """

    new_state = state.copy() if state else {}
    new_state["last_user_message"] = message
    msg = message.lower()

    # ---------- 1. Направления ----------
    if any(word in msg for word in ["море", "сочи", "отдых", "куда", "направление", "анапа", "геленджик"]):
        return AgentResponse(
            reply="Нашла несколько вариантов у моря. Выберите направление:",
            status="results",
            stage="destinations",
            updated_state=new_state,
            destinations=[
                {
                    "id": "sochi",
                    "name": "Сочи",
                    "reason": "Тёплое море, горы рядом, много отелей",
                    "price_from": 45000,
                    "currency": "RUB",
                },
                {
                    "id": "anapa",
                    "name": "Анапа",
                    "reason": "Мелкое море, подходит для семей с детьми",
                    "price_from": 32000,
                    "currency": "RUB",
                },
                {
                    "id": "geledzhik",
                    "name": "Геленджик",
                    "reason": "Красивые бухты и спокойный отдых",
                    "price_from": 38000,
                    "currency": "RUB",
                },
            ],
            warnings=["Данные синтетические (демо-режим)"],
        )

    # ---------- 2. Отели ----------
    if any(word in msg for word in ["отель", "отели", "выбираю", "гостиниц", "номер", "покажи"]):
        return AgentResponse(
            reply="Вот подходящие отели. Можно выбрать любой:",
            status="results",
            stage="hotels",
            updated_state=new_state,
            hotels=[
                {
                    "hotel_id": "h1",
                    "name": "Отель Морской Бриз",
                    "price": 8900,
                    "currency": "RUB",
                    "stars": 4,
                    "reason": "Рядом с пляжем, хороший завтрак",
                },
                {
                    "hotel_id": "h2",
                    "name": "Palm Resort",
                    "price": 12500,
                    "currency": "RUB",
                    "stars": 5,
                    "reason": "Бассейн, вид на море, спа",
                },
                {
                    "hotel_id": "h3",
                    "name": "Тихий берег",
                    "price": 7200,
                    "currency": "RUB",
                    "stars": 3,
                    "reason": "Недорогой вариант рядом с набережной",
                },
            ],
            warnings=["Данные синтетические (демо-режим)"],
        )

    # ---------- 3. Маршрут ----------
    if any(word in msg for word in ["маршрут", "план", "itin", "как добраться", "таймлайн"]):
        return AgentResponse(
            reply="Собрала предварительный маршрут:",
            status="results",
            stage="itinerary",
            updated_state=new_state,
            itinerary={
                "legs": [
                    {"type": "flight", "from": "Москва", "to": "Сочи", "time": "2ч 20м"},
                    {"type": "transfer", "from": "Аэропорт", "to": "Отель", "time": "40м"},
                    {"type": "hotel", "name": "Отель Морской Бриз", "nights": 5},
                ]
            },
            warnings=["Данные синтетические (демо-режим)"],
        )

    # ---------- 4. Корзина / оформление ----------
    if any(word in msg for word in ["корзина", "оформить", "бронь", "купить", "checkout", "подтверд"]):
        return AgentResponse(
            reply="Готово! Проверьте корзину и подтвердите демо-заказ.",
            status="results",
            stage="checkout",
            updated_state=new_state,
            cart={
                "items": [
                    {"name": "Перелёт Москва → Сочи", "price": 18000},
                    {"name": "Отель Морской Бриз, 5 ночей", "price": 44500},
                    {"name": "Трансфер", "price": 2500},
                ],
                "total": 65000,
                "currency": "RUB",
            },
            warnings=["Это демонстрационное бронирование. Реальной оплаты нет."],
        )

    # ---------- 5. Всё остальное — уточняем ----------
    return AgentResponse(
        reply="Расскажите подробнее: куда хотите поехать, на какие даты и какой бюджет?",
        status="clarification",
        stage="inspiration",
        updated_state=new_state,
        warnings=[],
    )


# ============================================================
# ПОЗЖЕ: подключение настоящего агента
# ============================================================
#
# Когда код агента и каталога появится в проекте, сделай так:
#
# 1. Раскомментируй импорты и создание агента:
#
# from backend.app.agent import AgentOrchestrator
# from backend.app.catalog.service import get_catalog_gateway
#
# catalog = get_catalog_gateway()
# agent = AgentOrchestrator(catalog=catalog)
#
# 2. Замени тело функции handle_message на:
#
# async def handle_message(
#     session_id: str,
#     message: str,
#     state: Dict[str, Any],
# ) -> AgentResponse:
#     result = await agent.handle_message(
#         session_id=session_id,
#         message=message,
#         state=state or {},
#     )
#     return result
#
# 3. Удали или закомментируй всю заглушку выше.
#
# ============================================================