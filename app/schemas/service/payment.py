from typing import Literal, Dict

from pydantic import BaseModel


class Amount(BaseModel):
    value: str
    currency: str


class Metadata(BaseModel):
    user_id: str
    quantity: int
    purchase_type: str
    bought_for: Literal["me"]


# class YookassaPaymentData(BaseModel):
#     amount: Amount
#     description: str
#     payment_method_id: str
#     capture: bool
#     metadata: Metadata


# class YookassaPaymentRequest(BaseModel):
#     payment_data: YookassaPaymentData
#     test: bool
#
#
# class PaymentNotification(BaseModel):
#     event: str
#     object: Dict