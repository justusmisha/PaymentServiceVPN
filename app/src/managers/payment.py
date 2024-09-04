import base64
import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Optional, Any, Union

import aiohttp
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import config
from app.database.methods.base import get_db
from app.database.methods.payment import get_transaction_by_id, get_discounts_and_promo

from app.database.methods.subscription import get_subscription
from app.database.methods.user import get_user
from app.app_logging import logger
from app.core.json_data.loads_json import json_data


class PaymentManager:
    """
    calculate_price - обращается к discount получая дискаунты юзера и расчитывает цену
    create_yookassa_payment - создает платеж в юкассе
    create_cryptomus_payment - создает платеж в cryptomus
    check_yookassa_payment - проверяет платеж, если нет в базе, то проверяет в юкассе и возвращает статус или платеж
    check_cryptomus_payment - проверяет платеж в базе и возвращает статус или платеж
    extract_from_yookassa - достает нужные данные из транзакции юкассы
    extract_from_cryptomus - достает нужные данные из транзакции криптомус
    save_transaction - сохраняет транзакцию в бд
    save_payment_method - сохраняет платежный метод в бд
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def calculate_price(self, db: AsyncSession, user_id: str, item: str, quantity: Optional[int] = 1, gift=False,
                              ) -> Optional[Dict[str, Any]]:
        quantity = str(quantity)
        if quantity not in json_data['prices'][item]:
            logger.error(f'Error calculating price for {item}: {quantity}. UserId: {user_id}')
            return None

        base_price = json_data['prices'][item][quantity]

        user = await get_user(user_id, db)

        if item == "default_to_family":
            base_price = await self._calculate_base_price_for_family(user.subs_id, base_price, db=db)
            if base_price is None:
                logger.error(f'Error calculating price: Could not calculate base price for family subscription')
                return None

        payment_id = user.payment_id
        discounts = await get_discounts_and_promo(payment_id, db)
        if not discounts:
            logger.error(f'Error calculating price: No payment details found for payment ID {payment_id}')
            return None

        personal_discount_info = discounts['personal_discount']
        general_discount_info = discounts['general_discount']
        promo_code_info = discounts['promo_code']

        if gift:
            personal_discount = personal_discount_info.discount_gift if personal_discount_info else 0
            general_discount = general_discount_info.discount_gift if general_discount_info else 0
        else:
            personal_discount, general_discount = self._calculate_discounts(item, personal_discount_info,
                                                                            general_discount_info)

        general_discount += promo_code_info.discount if promo_code_info else 0
        total_discount = min(personal_discount + general_discount, 70)
        price = int(base_price * (1 - total_discount / 100))

        return {
            "base_price": base_price,
            "personal_discount": personal_discount,
            "general_discount": general_discount,
            "total_discount": total_discount,
            "price": price
        }

    async def create_yookassa_payment(self, metadata: Dict, db: AsyncSession) -> Optional[Dict[str, Any]]:
        payment_data = await self._prepare_yookassa_payment_data(metadata, db)
        if not payment_data:
            return None

        headers = self._get_headers_yookassa()

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(config.YOOKASSA_API_URL, headers=headers, json=payment_data) as response:
                    logger.info(await response.text())
                    response.raise_for_status()
                    return await response.json()
            except Exception as e:
                logger.error(f"Error creating yookassa payment: {e}")
                return None

    async def create_cryptomus_payment(self, metadata: Dict, db: AsyncSession) -> Optional[Dict[str, Any]]:
        payment_data = await self._prepare_cryptomus_payment_data(metadata, db)
        if not payment_data:
            return None

        api_url = config.CRYPTOMUS_API_URL

        serialized_data, headers = self._get_headers_and_data_cryptomus(payment_data)
        print(serialized_data, headers)
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(api_url, headers=headers, data=serialized_data) as response:
                    logger.info(await response.text())
                    response.raise_for_status()
                    return await response.json()
            except Exception as e:
                logger.error(f"Error creating cryptomus payment: {e}")
                return None

    async def check_yookassa_payment(self, payment_id: str) -> Optional[Dict[str, Any]]:
        payment_data = await get_transaction_by_id(payment_id)

        if payment_data:
            result = {"status": "db_confirmed", "payment_data": payment_data}
        else:
            headers = self._get_headers_yookassa()

            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(f"{config.YOOKASSA_API_URL}/{payment_id}", headers=headers) as response:
                        response.raise_for_status()
                        payment_data = await response.json()
                except Exception as e:
                    logger.error(f"Error getting yookassa payment: {e}")
                    return None

            if payment_data.get("paid") and payment_data.get("status") == 'succeeded':
                result = {"status": "yookassa_confirmed", "payment_data": payment_data}
            else:
                result = {"status": "not_found", "payment_data": ""}

        return result

    async def check_cryptomus_payment(self, payment_id: str) -> Optional[Dict[str, Any]]:
        payment_data = await get_transaction_by_id(payment_id)
        if not payment_data:
            logger.error("Transaction not found in database")
            return {"status": "not_found", "payment_data": ""}

        return {"status": "db_confirmed", "payment_data": payment_data}

    # async def save_transaction(self, payment_id: str,
    #                            payment_amount: float,
    #                            user_id: str,
    #                            create_date: str,
    #                            pay_date: str,
    #                            currency: str,
    #                            pay_system: str,
    #                            method: str,
    #                            quantity: int,
    #                            purchase_type: str,
    #                            bought_for: str) -> Optional[bool]:
    #     try:
    #         create_date_dt = datetime.fromisoformat(create_date.rstrip('Z'))
    #         pay_date_dt = datetime.fromisoformat(pay_date.rstrip('Z'))
    #     except ValueError as e:
    #         logger.error(f'Error parsing date strings: {e}')
    #         return None
    #
    #     transaction_data = {
    #         "id": payment_id,
    #         "amount": payment_amount,
    #         "user_id": user_id,
    #         "create_date": create_date_dt,
    #         "pay_date": pay_date_dt,
    #         "currency": currency,
    #         "pay_system": pay_system,
    #         "method": method,
    #         "quantity": quantity,
    #         "purchase_type": purchase_type,
    #         "bought_for": bought_for
    #     }
    #
    #     result = await save_transaction(transaction_data)
    #
    #     if not result:
    #         logger.error(f'Cannot save transaction {payment_id}')
    #         return None
    #
    #     return True

    # async def save_payment_method(self, user_id: str,
    #                               payment_method_id: str,
    #                               purchase_type: str,
    #                               quantity: int,
    #                               currency: str,
    #                               bought_for: str) -> Optional[bool]:
    #
    #     user = await get_user(user_id)
    #
    #     if bought_for == "me":
    #         if purchase_type == "test":
    #             quantity = 1
    #             purchase_type = "default"
    #         if purchase_type == "default_to_family":
    #             quantity = 1
    #             purchase_type = "family"
    #
    #         calculate_price = await self.calculate_price(user_id, purchase_type, quantity)
    #
    #         if not calculate_price:
    #             logger.error(f'Cannot calculate price for user {user_id}')
    #             return None
    #
    #         amount = {"value": calculate_price['price'], "currency": currency}
    #         capture = config.YOOKASSA_CAPTURE
    #         description = config.YOOKASSA_DESCRIPTION
    #         metadata = {"user_id": user_id,
    #                     "quantity": quantity,
    #                     "purchase_type": purchase_type,
    #                     "bought_for": "me"}
    #         yookassa_payment_data = {"amount": amount,
    #                                  "capture": capture,
    #                                  "description": description,
    #                                  "metadata": metadata,
    #                                  "payment_method_id": payment_method_id}
    #
    #         await save_yookassa_payment(user.payment_id, yookassa_payment_data)
    #         return True
    #
    #     return False

    def extract_from_yookassa(self, payment: Dict) -> Optional[Dict]:
        result_payment = {}
        if payment['paid'] is not True:
            return None

        if payment['status'] != 'succeeded':
            return None

        result_payment['id'] = payment['id']
        result_payment['amount'] = float(payment['amount']['value'])
        result_payment['create_date'] = payment['created_at']
        result_payment['pay_date'] = payment['captured_at']
        result_payment['currency'] = payment['amount']['currency']
        result_payment['pay_system'] = "yookassa"
        result_payment['method'] = payment['payment_method']['type']
        result_payment['user_id'] = payment['metadata']['user_id']
        result_payment['quantity'] = payment['metadata']['quantity']
        result_payment['purchase_type'] = payment['metadata']['purchase_type']
        result_payment['bought_for'] = payment['metadata']['bought_for']

        payment_method_id = None
        if payment['payment_method']['saved'] is True:
            payment_method_id = payment['payment_method']['id']

        result_payment['payment_method_id'] = payment_method_id

        return result_payment

    def extract_from_cryptomus(self, payment: Dict) -> Optional[Dict]:
        result_payment = {}
        if payment['status'] != 'paid':
            return None

        current_time = datetime.now(timezone.utc)
        current_time_str = current_time.isoformat()

        result_payment['id'] = payment['uuid']
        result_payment['amount'] = float(payment['amount'])
        result_payment['create_date'] = current_time_str
        result_payment['pay_date'] = current_time_str
        result_payment['currency'] = payment['currency']
        result_payment['pay_system'] = "cryptomus"
        result_payment['method'] = payment['network']

        additional_data = json.loads(payment['additional_data'])

        result_payment['user_id'] = additional_data['user_id']
        result_payment['quantity'] = additional_data['quantity']
        result_payment['purchase_type'] = additional_data['purchase_type']
        result_payment['bought_for'] = additional_data['bought_for']

        payment_method_id = None
        result_payment['payment_method_id'] = payment_method_id

        return result_payment

    async def _prepare_yookassa_payment_data(self, metadata: Dict, db: AsyncSession) -> Optional[Dict[str, Any]]:
        user_id = metadata['user_id']
        purchase_type = metadata['purchase_type']
        bought_for = metadata.get('bought_for')
        quantity = metadata.get('quantity', 0)
        return_url = metadata.get('return_url')
        save_payment = metadata.get('save_payment')

        gift = False
        if bought_for == "gift":
            gift = True

        price = await self.calculate_price(db, user_id, purchase_type, quantity, gift)
        if not price:
            return None

        amount = {
            "value": f"{price['price']}",
            "currency": "RUB"
        }

        payment_metadata = {
            "user_id": user_id,
            "quantity": quantity,
            "purchase_type": purchase_type,
            "bought_for": bought_for
        }

        confirmation = {
            "type": "redirect",
            "return_url": return_url
        }
        save_payment_method = save_payment
        if bought_for == "gift" or purchase_type == "traffic":
            save_payment_method = False

        bought_for_message = "личного" if bought_for == "me" else "подарочного"
        purchase_type_message = "Траффик" if purchase_type == 'traffic' else "Подписка"
        quantity_message = f'{quantity} Гб.' if purchase_type == "traffic" else f'{quantity} мес.'

        data = {
            "amount": amount,
            "description": f"Оплата {bought_for_message} товара. Тип товара: {purchase_type_message}. "
                           f"Кол-во: {quantity_message}",
            "confirmation": confirmation,
            "save_payment_method": save_payment_method,
            "capture": True,
            "metadata": payment_metadata,
        }

        return data

    async def _prepare_cryptomus_payment_data(self, metadata: Dict, db: AsyncSession) -> Optional[Dict[str, Any]]:
        user_id = metadata['user_id']
        purchase_type = metadata['purchase_type']
        bought_for = metadata.get('bought_for')
        quantity = metadata.get('quantity')
        return_url = metadata.get('return_url')

        item = purchase_type
        if bought_for == "gift":
            item = "gift"

        price = await self.calculate_price(db, user_id, item, quantity)
        if not price:
            return None

        payment_metadata = {
            "user_id": user_id,
            "quantity": quantity,
            "purchase_type": purchase_type,
            "bought_for": bought_for
        }

        payment_data = {
            "amount": f"{price['price']}",
            "currency": "RUB",
            "order_id": f"{uuid.uuid4()}",
            "additional_data": json.dumps(payment_metadata),
            "url_return": return_url,
            "url_callback": config.CRYPTOMUS_URL_CALLBACK,
            "url_success": return_url
        }

        return payment_data

    @staticmethod
    def _get_headers_yookassa() -> Dict[str, str]:
        shop_id = config.YOOKASSA_SHOP_ID
        api_key = config.YOOKASSA_API_KEY

        auth_header = base64.b64encode(f"{shop_id}:{api_key}".encode()).decode()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {auth_header}",
            "Idempotence-Key": str(uuid.uuid4())
        }

        return headers

    @staticmethod
    def _get_headers_and_data_cryptomus(payment_data: Dict) -> (str, Dict[str, str]):
        api_key = config.CRYPTOMUS_API_KEY

        serialized_data = json.dumps(payment_data, separators=(',', ':'))

        sign = hashlib.md5(
            (base64.b64encode(serialized_data.encode('utf-8')).decode('utf-8') + api_key).encode('utf-8')).hexdigest()

        headers = {
            "merchant": config.CRYPTOMUS_MERCHANT_ID,
            "Content-Type": "application/json",
            "sign": sign
        }

        return serialized_data, headers

    @staticmethod
    def _calculate_discounts(item: str, personal_discount_info,
                             general_discount_info) -> (int, int):
        personal_discount = 0
        general_discount = 0

        if item == "default":
            personal_discount = personal_discount_info.discount_default if personal_discount_info else 0
            general_discount = general_discount_info.discount_default if general_discount_info else 0
        elif item == "family":
            personal_discount = personal_discount_info.discount_family if personal_discount_info else 0
            general_discount = general_discount_info.discount_family if general_discount_info else 0
        elif item == "traffic":
            personal_discount = personal_discount_info.discount_traffic if personal_discount_info else 0
            general_discount = general_discount_info.discount_traffic if general_discount_info else 0
        elif item == "default_to_family":
            personal_discount = personal_discount_info.discount_default_to_family if personal_discount_info else 0
            general_discount = general_discount_info.discount_default_to_family if general_discount_info else 0

        personal_discount += personal_discount_info.onetime_discount if personal_discount_info else 0
        general_discount += general_discount_info.onetime_discount if general_discount_info else 0

        return personal_discount, general_discount

    @staticmethod
    async def _calculate_base_price_for_family(subs_id: Optional[int], base_price: float, db: AsyncSession) -> Optional[float]:
        current_date = datetime.today().date()

        subscription = await get_subscription(subs_id, db)
        if not subscription:
            return None

        date_stop = subscription['date_stop']

        if isinstance(date_stop, datetime):
            date_stop = date_stop.date()

        delta = (date_stop - current_date).days
        return base_price * delta
