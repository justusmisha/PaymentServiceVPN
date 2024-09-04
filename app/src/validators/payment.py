from datetime import datetime
from typing import Dict

from fastapi import HTTPException

from app.core.config import TRAFFIC_TEST, SERVICE_TEST
from app.schemas.user.subscriptions import SubscriptionResponse
from app.schemas.user.users import UserResponse


class PaymentValidator:
    def __init__(self):
        pass

    @staticmethod
    def can_buy_with_sub(subscription: SubscriptionResponse, purchase_type: str, bought_for: str) -> bool:
        if bought_for == "gift":
            valid_purchase_types = ['default', 'family']
            if not TRAFFIC_TEST:
                valid_purchase_types.append('traffic')
            if SERVICE_TEST:
                valid_purchase_types.append('traffic')
            if purchase_type not in valid_purchase_types:
                return False
        else:
            if subscription.subscription_type.default_subs.owner_id:
                return False
            if subscription.subscription_type.family_subs:
                valid_purchase_types = ['family']
                if not TRAFFIC_TEST:
                    valid_purchase_types.append('traffic')
                if SERVICE_TEST:
                    valid_purchase_types.append('traffic')

                if purchase_type not in valid_purchase_types:
                    return False
            else:
                valid_purchase_types = ['default', 'default_to_family']
                if not TRAFFIC_TEST:
                    valid_purchase_types.append('traffic')
                if SERVICE_TEST:
                    valid_purchase_types.append('traffic')

                if purchase_type not in valid_purchase_types:
                    return False

        return True

    @staticmethod
    def can_buy_without_sub(user: UserResponse, purchase_type: str, bought_for: str) -> bool:
        if bought_for == "gift":
            valid_purchase_types = ['default', 'family']
            if not TRAFFIC_TEST:
                valid_purchase_types.append('traffic')
            if SERVICE_TEST:
                valid_purchase_types.append('traffic')
            if purchase_type not in valid_purchase_types:
                return False
        else:
            valid_purchase_types = ['default', 'family']
            if user.test_available:
                valid_purchase_types.append('test')

            if purchase_type not in valid_purchase_types:
                return False

        return True

    @staticmethod
    def discount_info(discount_info: Dict[str, any]) -> bool:
        if discount_info.get('date_start') and discount_info['date_start'].date() > datetime.now().date():
            return False
        if discount_info.get('date_stop') and discount_info['date_stop'].date() < datetime.now().date():
            return False

        return True
