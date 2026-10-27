
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, ConfigDict


class ChatRequest(BaseModel):
    """Проверяет сообщение, которое присылает frontend."""

    model_config = ConfigDict(str_strip_whitespace=True)

    session_id: Optional[str] = Field(
        default=None,
        description="ID существующей сессии или null для новой",
    )
    message: str = Field(
        min_length=1,
        max_length=4000,
        description="Новое сообщение пользователя",
    )


class HotelCard(BaseModel):
    """Публичная карточка отеля для frontend."""

    hotel_id: str
    name: str
    price: Optional[float] = None
    currency: str = "RUB"


class ChatResponse(BaseModel):
    """Публичный ответ backend."""

    session_id: str
    status: Literal[
        "clarification",
        "results",
        "no_results",
        "error",
    ]
    reply: str
    hotels: List[HotelCard] = Field(default_factory=list)

    # временно оставляем
    state: Dict[str, Any] = Field(default_factory=dict)

    # --- новые поля ---
    stage: Optional[str] = None
    destinations: List[Dict[str, Any]] = Field(default_factory=list)
    itinerary: Optional[Dict[str, Any]] = None
    cart: Optional[Dict[str, Any]] = None
    warnings: List[Dict[str, Any]] = Field(default_factory=list)
    is_demo: bool = True