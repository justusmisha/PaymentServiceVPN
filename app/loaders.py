from fastapi import Depends

from app.database.methods.base import get_db
from app.src.managers.payment import PaymentManager
from app.src.validators.payment import PaymentValidator


payment_validator = PaymentValidator()
payment_manager = PaymentManager(Depends(get_db))