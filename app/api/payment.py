from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.methods.base import get_db
from app.database.methods.subscription import get_subscription
from app.database.methods.user import get_user
from app.database.models import Users
from app.loaders import payment_validator, payment_manager
from app.core.json_data.loads_json import json_data
from app.schemas.user.payments import (Prices, YookassaResponse, MetadataRequest, CryptomusResponse,
                                       AvailableTypesResponse)


router = APIRouter()


@router.get("/available_types/me", response_model=AvailableTypesResponse)
async def get_available_types_me_route(user_id: str, db: AsyncSession = Depends(get_db)):
    # Проверка, доступен ли тест
    user = await get_user('1', db)
    subs_id = user.subs_id
    # Если подписки нет
    if not subs_id:
        # Используем PaymentValidator для проверки возможных покупок без подписки
        default_available = payment_validator.can_buy_without_sub(user, "default", "me")
        family_available = payment_validator.can_buy_without_sub(user, "family", "me")
        test_available = payment_validator.can_buy_without_sub(user, "test", "me")
        default_to_family_available = payment_validator.can_buy_without_sub(user, "default_to_family", "me")
        traffic_available = payment_validator.can_buy_without_sub(user, "traffic", "me")

        result = AvailableTypesResponse(
            default=default_available,
            family=family_available,
            default_to_family=default_to_family_available,
            traffic=traffic_available,
            test=test_available
        )
        return result

    # Если подписка существует
    subscription = await get_subscription(user.subs_id, db)

    default_available = payment_validator.can_buy_with_sub(subscription, "default", "me")
    family_available = payment_validator.can_buy_with_sub(subscription, "family", "me")
    default_to_family_available = payment_validator.can_buy_with_sub(subscription, "default_to_family", "me")
    traffic_available = payment_validator.can_buy_with_sub(subscription, "traffic", "me")
    test_available = payment_validator.can_buy_without_sub(subscription, "test", "me")

    result = AvailableTypesResponse(
        default=default_available,
        family=family_available,
        default_to_family=default_to_family_available,
        traffic=traffic_available,
        test=test_available
    )
    return result


@router.get("/available_types/gift", response_model=AvailableTypesResponse)
async def get_available_types_gift_route():
    result = AvailableTypesResponse(default=True,
                                    family=True,
                                    default_to_family=False,
                                    traffic=True,
                                    test=False)
    return result


@router.get("/prices", response_model=Prices)
async def get_prices_route():
    prices = json_data.get('prices')
    return Prices(default=prices.get('default'), family=prices.get('family'),
                  default_to_family=prices.get('default_to_family'), traffic=prices.get('traffic'))


@router.post("/yookassa/create/", response_model=YookassaResponse)
async def create_yookassa_payment_route(metadata_request: MetadataRequest, db: AsyncSession = Depends(get_db)):
    payment = await payment_manager.create_yookassa_payment(metadata_request.model_dump(), db)
    if not payment:
        raise HTTPException(status_code=500, detail="Payment creation failed")

    return YookassaResponse(**payment)


@router.post("/cryptomus/create/", response_model=CryptomusResponse)
async def create_cryptomus_payment_route(metadata_request: MetadataRequest, db: AsyncSession = Depends(get_db)):
    payment = await payment_manager.create_cryptomus_payment(metadata_request.model_dump(), db)
    if not payment:
        raise HTTPException(status_code=500, detail="Payment creation failed")

    return CryptomusResponse(**payment)


@router.get("/test_db", response_model=bool)
async def test_db(db: AsyncSession = Depends(get_db)):
    await get_subscription(1, db)
    return True

