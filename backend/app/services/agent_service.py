"""
Сейчас здесь умная заглушка, которая имитирует разные стадии,
чтобы Frontend мог работать.

Когда появится настоящий агент (backend.app.agent),
нужно будет раскомментировать блок внизу и убрать заглушку.
"""

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class AgentResponse(BaseModel):
    """То, что возвращает AI-агент (и наша заглушка тоже)."""

    status: Literal["clarification", "results", "no_results", "error"]
    reply: str
    hotels: List[Dict[str, Any]] = Field(default_factory=list)
    updated_state: Dict[str, Any] = Field(default_factory=dict)
    stage: Optional[str] = None
    destinations: List[Dict[str, Any]] = Field(default_factory=list)
    transport_options: List[Dict[str, Any]] = Field(default_factory=list)
    itinerary: Optional[Dict[str, Any]] = None
    cart: Optional[Dict[str, Any]] = None
    warnings: List[str] = Field(default_factory=list)


def _demo_destinations() -> list:
    return [
        {
            "id": "sochi",
            "name": "Сочи",
            "country": "Россия",
            "avg_temp_c": 18,
            "flight_hours": 2.3,
            "price_from": 45000,
            "currency": "RUB",
            "why": "Тёплое море, горы рядом, много отелей",
            "tags": ["море", "горы", "семьи"],
            "is_demo": True,
        },
        {
            "id": "anapa",
            "name": "Анапа",
            "country": "Россия",
            "avg_temp_c": 16,
            "flight_hours": 2.0,
            "price_from": 32000,
            "currency": "RUB",
            "why": "Мелкое море, подходит для детей",
            "tags": ["море", "дети", "бюджет"],
            "is_demo": True,
        },
        {
            "id": "spb",
            "name": "Санкт-Петербург",
            "country": "Россия",
            "avg_temp_c": 5,
            "flight_hours": 1.5,
            "price_from": 28000,
            "currency": "RUB",
            "why": "Культура, выходные, удобный перелёт",
            "tags": ["город", "культура", "выходные"],
            "is_demo": True,
        },
    ]


def _demo_hotels() -> list:
    return [
        {
            "hotel_id": "h1",
            "name": "Отель Морской Бриз",
            "city": "Сочи",
            "price": 8900,
            "price_total": 44500,
            "currency": "RUB",
            "nights": 5,
            "stars": 4,
            "reason": "Рядом с пляжем, хороший завтрак",
            "is_demo": True,
        },
        {
            "hotel_id": "h2",
            "name": "Palm Resort",
            "city": "Сочи",
            "price": 12500,
            "price_total": 62500,
            "currency": "RUB",
            "nights": 5,
            "stars": 5,
            "reason": "Бассейн, вид на море, спа",
            "is_demo": True,
        },
        {
            "hotel_id": "h3",
            "name": "Тихий берег",
            "city": "Сочи",
            "price": 7200,
            "price_total": 36000,
            "currency": "RUB",
            "nights": 5,
            "stars": 3,
            "reason": "Недорогой вариант у набережной",
            "is_demo": True,
        },
    ]


async def handle_message(
    session_id: str,
    message: str,
    state: Dict[str, Any],
) -> AgentResponse:
    new_state = state.copy() if state else {}
    new_state["last_user_message"] = message
    msg = message.lower().strip()

    # 1. Выбор направления с карточки
    if msg.startswith("выбираю направление"):
        name = message.split(":", 1)[-1].strip()
        new_state["selected_destination_name"] = name
        return AgentResponse(
            reply=f"Отлично, ищем жильё в направлении: {name}",
            status="results",
            stage="hotels",
            updated_state=new_state,
            hotels=_demo_hotels(),
            warnings=["Данные синтетические (демо-режим)"],
        )

    # 2. Выбор отеля с карточки
    if msg.startswith("выбираю отель"):
        name = message.split(":", 1)[-1].strip()
        new_state["selected_hotel_name"] = name
        return AgentResponse(
            reply=f"Отель «{name}» выбран. Собираю маршрут и корзину.",
            status="results",
            stage="checkout",
            updated_state=new_state,
            itinerary={
                "legs": [
                    {"type": "flight", "from": "Москва", "to": "Сочи", "time": "2ч 20м"},
                    {"type": "transfer", "from": "Аэропорт", "to": "Отель", "time": "40м"},
                    {"type": "hotel", "name": name, "nights": 5},
                ]
            },
            cart={
                "items": [
                    {"name": "Перелёт Москва → Сочи", "price": 18000},
                    {"name": f"Отель {name}, 5 ночей", "price": 44500},
                    {"name": "Трансфер", "price": 2500},
                ],
                "total": 65000,
                "currency": "RUB",
            },
            warnings=["Это демонстрационное бронирование. Реальной оплаты нет."],
        )

    # 3. Направления
    if any(w in msg for w in ["море", "сочи", "отдых", "куда", "направление", "анапа", "геленджик", "питер", "петербург"]):
        return AgentResponse(
            reply="Нашла несколько вариантов. Выберите направление:",
            status="results",
            stage="destinations",
            updated_state=new_state,
            destinations=_demo_destinations(),
            warnings=["Данные синтетические (демо-режим)"],
        )

    # 4. Отели
    if any(w in msg for w in ["отель", "отели", "гостиниц", "номер", "покажи", "жильё", "жилье"]):
        return AgentResponse(
            reply="Вот подходящие отели:",
            status="results",
            stage="hotels",
            updated_state=new_state,
            hotels=_demo_hotels(),
            warnings=["Данные синтетические (демо-режим)"],
        )

    # 5. Маршрут
    if any(w in msg for w in ["маршрут", "план", "таймлайн", "как добраться"]):
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

    # 6. Корзина
    if any(w in msg for w in ["корзина", "оформить", "бронь", "купить", "checkout", "подтверд"]):
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

    # 7. Fallback — ВСЕГДА должен быть return
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
# Когда появятся пакеты backend.app.agent и backend.app.catalog:
#
# 1. В начале файла раскомментируй:
#
# from backend.app.agent import AgentOrchestrator
# from backend.app.catalog.service import get_catalog_gateway
#
# catalog = get_catalog_gateway()
# agent = AgentOrchestrator(catalog=catalog)
#
# 2. Замени тело handle_message на:
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
# 3. Старую заглушку (все if-ветки) можно удалить или закомментировать.
#
# ============================================================