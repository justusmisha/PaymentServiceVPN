import json

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.methods.base import get_db
from app.database.models import Subscription, SubsType, SubsDefault
from app.schemas.user.subscriptions import SubscriptionResponse
from app.app_logging import logger


async def get_subscription(subscription_id: int, db: AsyncSession) -> SubscriptionResponse:
    try:
        result = await db.execute(
            select(Subscription)
            .options(
                selectinload(Subscription.subscription_type)
                .selectinload(SubsType.default_subscription),
                selectinload(Subscription.subscription_type)
                .selectinload(SubsType.family_subscription)
            )
            .where(Subscription.id == subscription_id)
        )
        subscription = result.scalar_one_or_none()

        if subscription is None:
            logger.warning(f"Subscription with ID {subscription_id} not found.")
            raise HTTPException(status_code=404, detail="❌ Подписка не найдена")
        result2 = await db.execute(
            select(SubsDefault).where(SubsDefault.id == subscription.subscription_type.default_subs)
        )
        subs_default = result2.scalar_one_or_none()
        subscription_data = {
            "id": subscription.id,
            "date_start": subscription.date_start,
            "date_stop": subscription.date_stop,
            "type": subscription.type,
            "is_test": subscription.is_test,
            "subscription_type": {
                "id": subscription.subscription_type.id,
                "default_subs": subs_default,
                "family_subs": subscription.subscription_type.family_subs
            }
        }
        logger.info(f"Subscription data: {json.dumps(subscription_data, default=str)}")
        return SubscriptionResponse.from_orm(subscription)
    except SQLAlchemyError as e:
        logger.error(f"Database error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
