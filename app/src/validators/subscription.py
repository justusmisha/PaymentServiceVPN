from fastapi import APIRouter, Depends, HTTPException

from app.core.config import TRAFFIC_TEST
from app.schemas.user.subscriptions import SubscriptionResponse
from app.app_logging import logger


class SubscriptionValidator:
    def __init__(self):
        pass

    @staticmethod
    def create_family_link(subscription: SubscriptionResponse, traffic_limit_mb: int, name: str) -> bool:
        if not subscription.subscription_type.family_link:
            raise HTTPException(status_code=400, detail="❌ Для создания ссылок нужна семейная подписка")

        if len(name) > 4:
            raise HTTPException(status_code=400, detail="❌ Длина имени должна быть не более 4 символов")

        if not TRAFFIC_TEST:
            remain_traffic_mb = (subscription.traffic_limit_mb -
                                 (subscription.outline_details.traffic_mb + subscription.vless_details.traffic_mb))

            if traffic_limit_mb > remain_traffic_mb:
                raise HTTPException(status_code=400, detail=f"❌ Вы не можете указать больше траффика чем у вас есть")

        return True

    @staticmethod
    def change_location(subscription: SubscriptionResponse) -> bool:
        total_traffic_mb = subscription.outline_details.traffic_mb + subscription.vless_details.traffic_mb

        if total_traffic_mb > subscription.traffic_limit_mb:
            raise HTTPException(status_code=400, detail="❌ Вы не можете изменить локацию, "
                                                        "тк у вас закончился лимит траффика")

        return True

    @staticmethod
    def process_family_link(subscription: SubscriptionResponse, traffic_limit_mb: int, name: str) -> bool:
        if not subscription.subscription_type.family_subs:
            raise HTTPException(status_code=400, detail="❌ Нельзя использовать ссылку, "
                                                        "тк пользватель который вам предоставил"
                                                        " больше не обладает семейной подпиской")

        remained_traffic_mb = subscription.traffic_limit_mb - (subscription.outline_details.traffic_mb
                                                               + subscription.vless_details.traffic_mb)

        if traffic_limit_mb > remained_traffic_mb:
            raise HTTPException(status_code=400, detail="❌ Невозможно использовать ссылку, "
                                                        "тк у владельца подписки нет столько траффика")

        family_data = subscription.subscription_type.family_subs.family_data
        if family_data and len(family_data) > 5:
            raise HTTPException(status_code=400, detail="❌ Владелец семеной подписки достиг лимита пользователей")

        if name in family_data:
            raise HTTPException(status_code=400, detail="❌ Ссылка с этим именем уже использована")

        return True

