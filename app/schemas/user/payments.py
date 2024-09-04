from typing import Dict, Optional, Literal, Any, List

from pydantic import BaseModel


class AvailableTypesResponse(BaseModel):
    default: bool
    family: bool
    default_to_family: bool
    traffic: bool
    test: bool


class Prices(BaseModel):
    default: Dict[str, int]
    family: Dict[str, int]
    traffic: Dict[str, int]
    default_to_family: Dict[str, int]


class MetadataRequest(BaseModel):
    user_id: str
    purchase_type: str
    quantity: Optional[str]
    return_url: str
    bought_for: Literal["me", "gift"]
    save_payment: bool


class Amount(BaseModel):
    value: str
    currency: str


class Confirmation(BaseModel):
    type: str
    confirmation_url: str


class YookassaResponse(BaseModel):
    id: str
    status: str
    amount: Amount
    created_at: str
    confirmation: Confirmation
    test: bool
    paid: bool
    metadata: Dict


class CryptomusResult(BaseModel):
    uuid: str
    payment_status: str
    amount: str
    currency: str
    created_at: str
    url: str
    additional_data: Any


class CryptomusResponse(BaseModel):
    state: int
    result: CryptomusResult


# class PromocodeProcessRequest(BaseModel):
#     user_id: str
#     name: str
#
#
# class Discount(BaseModel):
#     family: Optional[int]
#     default: Optional[int]
#     traffic: Optional[int]
#     gift: Optional[int]
#     default_to_family: Optional[int]
#     onetime: Optional[int]
#
#
# class PromoCode(BaseModel):
#     name: str
#     discount: int
#
#
# class DiscountsResponse(BaseModel):
#     personal_discount: Optional[Discount]
#     general_discount: Optional[Discount]
#     promo_code_discount: Optional[PromoCode]
#
#
# class TransactionResponse(BaseModel):
#     id: str
#     amount: float
#     create_date: datetime
#     pay_date: Optional[datetime]
#     currency: str
#     pay_system: str
#     method: str
#     quantity: int
#     purchase_type: str
#     bought_for: str
#
#     class Config:
#         orm_mode = True
#
#
# class TransactionListResponse(BaseModel):
#     transactions: List[TransactionResponse]