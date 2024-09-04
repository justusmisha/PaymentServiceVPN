from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserResponse(BaseModel):
    id: str
    start_date: datetime
    test_available: bool
    subs_id: Optional[int]
    payment_id: Optional[int]
    referal_to: Optional[str]  # ID того, кто пригласил пользователя

    class Config:
        from_attributes = True


class UserCreateRequest(BaseModel):
    user_id: str
