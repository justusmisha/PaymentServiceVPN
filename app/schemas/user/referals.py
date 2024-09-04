from pydantic import BaseModel
from typing import Optional, Dict


class ReferalData(BaseModel):
    referral_id: str
    points: int


# class ReferalsResponse(BaseModel):
#     referal_data: Optional[Dict[str, ReferalData]]
#     referrer_id: Optional[str]  # ID того, кто пригласил пользователя
#
#
# class ReferalLinkResponse(BaseModel):
#     argument: str
#
#
# class ProcessLinkRequest(BaseModel):
#     user_id: str
#     message: str
#
#
# class AvailableTypesResponse(BaseModel):
#     default: bool
#     family: bool
#     traffic: bool
#
#
# class ExchangeRequest(BaseModel):
#     user_id: str
#     purchase_type: str
