from fastapi import APIRouter
from ..contracts.chat import ChatRequest, ChatResponse, HotelCard
from ..sessions.service import session_service
from ..services.agent_service import handle_message
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Главный эндпоинт.
    Принимает сообщение → вызывает агента → сохраняет всё → отдаёт ответ.
    """

    # 1. Сессия
    if request.session_id:
        session = session_service.get_session(request.session_id)
        if not session:
            session_id = session_service.create_session()
            state = {}
        else:
            session_id = request.session_id
            state = session.get("state", {})
    else:
        session_id = session_service.create_session()
        state = {}

    # 2. Сохраняем сообщение пользователя
    session_service.add_message(
        session_id=session_id,
        role="user",
        content=request.message
    )

    # Внутри endpoint, вместо прежнего вызова агента:
    try:
        agent_response = await handle_message(
            session_id=session_id,
            message=request.message,
            state=state,
        )
    except Exception:
        # Полный traceback остаётся в серверных логах,
        # но технические подробности не показываем пользователю.
        logger.exception(
            "Agent call failed for session_id=%s",
            session_id,
        )

        error_reply = (
            "Не удалось обработать сообщение. "
            "Попробуйте ещё раз."
        )

        session_service.add_message(
            session_id=session_id,
            role="assistant",
            content=error_reply,
        )

        return ChatResponse(
            session_id=session_id,
            status="error",
            reply=error_reply,
            hotels=[],
            state=state,
        )


    # 4. Сохраняем ответ агента и обновлённый state
    session_service.add_message(
        session_id=session_id,
        role="assistant",
        content=agent_response.reply
    )
    session_service.update_state(session_id, agent_response.updated_state)

    # 5. Отдаём ответ Frontend
    hotels = [
        HotelCard(
            hotel_id=h.get("hotel_id", ""),
            name=h.get("name", ""),
            price=h.get("price"),
            currency=h.get("currency", "RUB")
        )
        for h in agent_response.hotels
    ]

    return ChatResponse(
    session_id=session_id,
    status=agent_response.status,
    reply=agent_response.reply,
    hotels=hotels,
    state=agent_response.updated_state,
    stage=agent_response.stage,
    destinations=agent_response.destinations,
    itinerary=agent_response.itinerary,
    cart=agent_response.cart,
    warnings=[
    {"level": "info", "text": w} 
    for w in agent_response.warnings
    ],
    is_demo=True,
)