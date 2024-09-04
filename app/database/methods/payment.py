from typing import Dict

from fastapi import Depends, HTTPException
from sqlalchemy import update, delete, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.methods.base import get_db
from app.database.models import PaymentDetails, Users, Transactions
from app.app_logging import logger

#
# async def delete_yookassa_payment(paymentdetails_id: int, db: AsyncSession = Depends(get_db)) -> bool:
#     try:
#         # Шаг 1: Получаем yookassa_payment_id из PaymentDetails
#         result = await db.execute(
#             select(PaymentDetails.yookassa_payment_id)
#             .where(PaymentDetails.id == paymentdetails_id)
#         )
#         yookassa_payment_id = result.scalar_one_or_none()
#
#         if not yookassa_payment_id:
#             logger.warning(f"No YookassaPayment associated with PaymentDetails ID: {paymentdetails_id}")
#             raise HTTPException(status_code=404, detail="❌ Автоплатеж не найден")
#
#         # Шаг 2: Устанавливаем yookassa_payment_id в NULL в PaymentDetails
#         await db.execute(
#             update(PaymentDetails)
#             .where(PaymentDetails.id == paymentdetails_id)
#             .values(yookassa_payment_id=None)
#         )
#
#         # Шаг 3: Удаляем запись из YookassaPayments
#         result = await db.execute(
#             delete(YookassaPayments)
#             .where(YookassaPayments.id == yookassa_payment_id)
#         )
#
#         if result.rowcount == 0:
#             logger.warning(f"No YookassaPayments found with ID: {yookassa_payment_id}")
#             raise HTTPException(status_code=404, detail="❌ Запись YookassaPayments не найдена")
#
#         # Применяем изменения
#         await db.commit()
#
#         logger.info(f"YookassaPayments deleted and PaymentDetails updated successfully for PaymentDetails ID {paymentdetails_id}")
#         return True
#
#     except SQLAlchemyError as e:
#         await db.rollback()
#         logger.error(f"Failed to delete YookassaPayments for PaymentDetails ID {paymentdetails_id}: {e}")
#         raise HTTPException(status_code=500, detail="Internal Server Error")


# async def set_promocode(paymentdetails_id: int, promocode_name: str, db: AsyncSession = Depends(get_db)) -> bool:
#     try:
#         # Шаг 1: Проверяем, существует ли промокод с указанным именем
#         result = await db.execute(
#             select(Promocodes)
#             .where(Promocodes.name == promocode_name)
#         )
#         promocode = result.scalar_one_or_none()
#
#         if not promocode:
#             logger.warning(f"Promocode with name {promocode_name} not found.")
#             raise HTTPException(status_code=404, detail="❌ Промокод не найден")
#
#         # Шаг 2: Устанавливаем промокод для записи в PaymentDetails
#         result = await db.execute(
#             update(PaymentDetails)
#             .where(PaymentDetails.id == paymentdetails_id)
#             .values(promo_code=promocode.name)
#         )
#
#         if result.rowcount == 0:
#             logger.warning(f"No PaymentDetails found with ID: {paymentdetails_id}")
#             raise HTTPException(status_code=404, detail="❌ Не удалось установить промокод")
#
#         # Применяем изменения
#         await db.commit()
#
#         logger.info(f"Promocode {promocode_name} successfully applied to PaymentDetails ID {paymentdetails_id}")
#         return True
#
#     except SQLAlchemyError as e:
#         await db.rollback()
#         logger.error(f"Failed to set promocode {promocode_name} for PaymentDetails ID {paymentdetails_id}: {e}")
#         raise HTTPException(status_code=500, detail="Internal Server Error")


# async def get_transactions_by_user_id(user_id: str, db: AsyncSession = Depends(get_db)):
#     try:
#         # Проверяем, существует ли пользователь с указанным user_id
#         result = await db.execute(select(Users).where(Users.id == user_id))
#         user = result.scalar_one_or_none()
#
#         if not user:
#             logger.warning(f"User with ID {user_id} not found.")
#             raise HTTPException(status_code=404, detail="❌ Пользователь не найден")
#
#         # Получаем список транзакций для пользователя
#         result = await db.execute(
#             select(Transactions)
#             .where(Transactions.user_id == user_id)
#             .order_by(Transactions.create_date.desc())  # Сортируем по дате создания (от новых к старым)
#         )
#         transactions = result.scalars().all()
#
#         if not transactions:
#             logger.info(f"No transactions found for user ID {user_id}.")
#             return []
#
#         return transactions
#
#     except SQLAlchemyError as e:
#         logger.error(f"Failed to retrieve transactions for user {user_id}: {e}")
#         raise HTTPException(status_code=500, detail="Internal Server Error")


async def get_discounts_and_promo(payment_id: int, db: AsyncSession):
    try:
        from app.loaders import payment_validator

        # Извлекаем детали платежа по payment_id
        result = await db.execute(
            select(PaymentDetails)
            .options(
                selectinload(PaymentDetails.personal_discount),
                selectinload(PaymentDetails.general_discount),
                selectinload(PaymentDetails.promo_code_obj)
            )
            .where(PaymentDetails.id == payment_id)
        )
        payment_details = result.scalar_one_or_none()

        if not payment_details:
            logger.warning(f"Payment details not found for payment_id: {payment_id}")
            raise HTTPException(status_code=404, detail="❌ Платежная информация не найдена")

        # Проверяем валидность персональной скидки
        personal_discount = None
        if payment_details.personal_discount:
            personal_discount_info = {
                'date_start': payment_details.personal_discount.date_start,
                'date_stop': payment_details.personal_discount.date_stop
            }
            if payment_validator.discount_info(personal_discount_info):
                personal_discount = payment_details.personal_discount

        # Проверяем валидность общей скидки
        general_discount = None
        if payment_details.general_discount:
            general_discount_info = {
                'date_start': payment_details.general_discount.date_start,
                'date_stop': payment_details.general_discount.date_stop
            }
            if payment_validator.discount_info(general_discount_info):
                general_discount = payment_details.general_discount

        # Проверяем валидность промокода
        promo_code = None
        if payment_details.promo_code_obj:
            promo_code_info = {
                'date_start': payment_details.promo_code_obj.date_start,
                'date_stop': payment_details.promo_code_obj.date_stop
            }
            if payment_validator.discount_info(promo_code_info):
                promo_code = payment_details.promo_code_obj

        return {
            'personal_discount': personal_discount,
            'general_discount': general_discount,
            'promo_code': promo_code
        }

    except SQLAlchemyError as e:
        logger.error(f"Failed to retrieve discounts and promo code for payment_id {payment_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


async def get_transaction_by_id(transaction_id: str, db: AsyncSession = Depends(get_db)) -> Dict[str, any] or bool:
    try:
        # Выполняем запрос для получения транзакции по ID
        result = await db.execute(
            select(Transactions)
            .where(Transactions.id == transaction_id)
        )
        transaction = result.scalar_one_or_none()

        if not transaction:
            logger.warning(f"Transaction with ID {transaction_id} not found.")
            return False

        return {
            'id': transaction.id,
            'amount': transaction.amount,
            'user_id': transaction.user_id,
            'create_date': transaction.create_date,
            'pay_date': transaction.pay_date,
            'currency': transaction.currency,
            'pay_system': transaction.pay_system,
            'method': transaction.method,
            'quantity': transaction.quantity,
            'purchase_type': transaction.purchase_type,
            'bought_for': transaction.bought_for
        }

    except SQLAlchemyError as e:
        logger.error(f"Failed to retrieve transaction with ID {transaction_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# async def save_transaction(transaction_data: Dict[str, any], db: AsyncSession = Depends(get_db)) -> bool:
#     try:
#         # Создаем объект транзакции на основе переданных данных
#         transaction = Transactions(
#             id=transaction_data['id'],
#             amount=transaction_data['amount'],
#             user_id=transaction_data['user_id'],
#             create_date=transaction_data.get('create_date'),
#             pay_date=transaction_data.get('pay_date'),
#             currency=transaction_data['currency'],
#             pay_system=transaction_data['pay_system'],
#             method=transaction_data['method'],
#             quantity=transaction_data['quantity'],
#             purchase_type=transaction_data['purchase_type'],
#             bought_for=transaction_data['bought_for']
#         )
#
#         # Добавляем транзакцию в сессию
#         db.add(transaction)
#
#         # Применяем изменения
#         await db.commit()
#
#         return True
#     except SQLAlchemyError as e:
#         await db.rollback()
#         logger.error(f"Failed to save transaction for user {transaction_data['user_id']}: {e}")
#         raise HTTPException(status_code=500, detail="Internal Server Error")


# async def save_yookassa_payment(payment_id: int, meta_data: dict, db: AsyncSession = Depends(get_db)) -> bool:
#     try:
#         # Шаг 1: Создаем новую запись в YookassaPayments
#         new_payment = YookassaPayments(meta_data=meta_data)
#         db.add(new_payment)
#         await db.flush()  # Получаем сгенерированный ID для новой записи
#
#         # Шаг 2: Обновляем запись в PaymentDetails, присваивая yookassa_payment_id
#         await db.execute(
#             update(PaymentDetails)
#             .where(PaymentDetails.id == payment_id)
#             .values(yookassa_payment_id=new_payment.id)
#         )
#
#         # Применяем изменения в базе данных
#         await db.commit()
#
#         logger.info(f"YookassaPayments created and assigned to PaymentDetails ID {payment_id}")
#         return True
#
#     except SQLAlchemyError as e:
#         await db.rollback()
#         logger.error(f"Failed to create YookassaPayments and assign to PaymentDetails ID {payment_id}: {e}")
#         raise HTTPException(status_code=500, detail="Internal Server Error")


# async def get_yookassa_payment(payment_id: int, db: AsyncSession = Depends(get_db)):
#     try:
#         # Шаг 1: Получаем yookassa_payment_id из PaymentDetails
#         result = await db.execute(
#             select(PaymentDetails.yookassa_payment_id)
#             .where(PaymentDetails.id == payment_id)
#         )
#         yookassa_payment_id = result.scalar_one_or_none()
#
#         if not yookassa_payment_id:
#             logger.info(f"No YookassaPayment associated with PaymentDetails ID: {payment_id}")
#             return False
#
#         # Шаг 2: Получаем YookassaPayments по yookassa_payment_id
#         result = await db.execute(
#             select(YookassaPayments)
#             .where(YookassaPayments.id == yookassa_payment_id)
#         )
#         yookassa_payment = result.scalar_one_or_none()
#
#         if not yookassa_payment:
#             logger.info(f"YookassaPayment with ID {yookassa_payment_id} not found.")
#             return False
#
#         return yookassa_payment
#
#     except SQLAlchemyError as e:
#         logger.error(f"Failed to retrieve YookassaPayments for payment_id {payment_id}: {e}")
#         raise HTTPException(status_code=500, detail="Internal Server Error")