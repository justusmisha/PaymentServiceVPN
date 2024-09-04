from datetime import datetime
from fastapi import HTTPException
from fastapi.params import Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.methods.base import get_db
from app.database.models import Users, PaymentDetails
from app.schemas.user.users import UserCreateRequest, UserResponse
from app.app_logging import logger


async def get_user(user_id: str, db: AsyncSession) -> UserResponse:
    try:

        result = await db.execute(
            select(Users)
            .where(Users.id == user_id)
        )
        user = result.scalar_one_or_none()

        if user is None:
            logger.warning(f"User with ID {user_id} not found.")
            raise HTTPException(status_code=404, detail="❌ Пользователь не найден")

        return UserResponse.from_orm(user)
    except SQLAlchemyError as e:
        logger.error(f"Database error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    except Exception as e:
        logger.error(f"Some Error occured: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# async def create_user(user_request: UserCreateRequest, db: AsyncSession = Depends(get_db)):
#     user_id = user_request.user_id
#
#     result = await db.execute(select(Users).where(Users.id == user_id))
#     user = result.scalar_one_or_none()
#
#     if user:
#         logger.warning(f"User with ID {user_id} already exists.")
#         raise HTTPException(status_code=400, detail="❌ Пользователь уже существует")
#
#     try:
#         # Создаем запись в payment_details с NULL значениями
#         new_payment_details = PaymentDetails()
#         db.add(new_payment_details)
#         await db.flush()  # Применяем изменения, чтобы получить id нового payment_details
#
#         # Создаем пользователя, связанного с новым payment_details
#         new_user = Users(
#             id=user_id,
#             payment_id=new_payment_details.id,  # Привязываем payment_details к пользователю
#             start_date=datetime.utcnow(),
#         )
#         db.add(new_user)
#
#         # Применяем изменения и обновляем объект new_user
#         await db.commit()
#     except SQLAlchemyError as e:
#         await db.rollback()
#         logger.error(f"Failed to create user {user_id}: {e}")
#         raise HTTPException(status_code=500, detail="Cannot create user")
#
#     return True

