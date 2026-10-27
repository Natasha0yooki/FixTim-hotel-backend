from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

# подставь свой импорт session_service
from backend.app.sessions.service import session_service   # путь поправь под свой

router = APIRouter(prefix="/api/v1/checkout", tags=["checkout"])


class CheckoutRequest(BaseModel):
    session_id: str


class CheckoutResponse(BaseModel):
    status: str
    message: str
    is_demo: bool = True


@router.post("/confirm", response_model=CheckoutResponse)
async def confirm_checkout(request: CheckoutRequest):
    """
    Демо-подтверждение заказа.
    Никакой реальной оплаты нет.
    """
    session = session_service.get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Сессия не найдена")

    # Помечаем в state, что демо-заказ подтверждён
    state = session.get("state", {})
    state["demo_booked"] = True
    state["booking_status"] = "confirmed"
    session_service.update_state(request.session_id, state)

    return CheckoutResponse(
        status="ok",
        message="Демо-заказ успешно подтверждён. Это учебное бронирование.",
        is_demo=True,
    )
   