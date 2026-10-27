from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/v1", tags=["hotels"])


@router.get("/hotels/{hotel_id}")
async def get_hotel(hotel_id: str):
    """
    Получение информации об отеле.
    Пока работает как заглушка.
    """

    # Простая заглушка. Позже здесь будет вызов Hotel Service / Catalog
    if hotel_id == "not-found":
        raise HTTPException(status_code=404, detail="Отель не найден")

    return {
        "hotel_id": hotel_id,
        "name": f"Демо-отель {hotel_id}",
        "city": "Сочи",
        "stars": 4,
        "price_per_night": 7500,
        "currency": "RUB",
        "amenities": ["wifi", "breakfast", "pool"],
        "description": "Это демо-данные. Настоящий поиск подключится позже.",
        "source_type": "demo"
    }