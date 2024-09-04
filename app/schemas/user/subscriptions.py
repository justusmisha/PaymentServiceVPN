from datetime import date, datetime
from typing import Dict, Optional, List

from pydantic import BaseModel


class SubsDefaultResponse(BaseModel):
    id: int
    owner_id: Optional[str]

    class Config:
        from_attributes = True


class SubsFamilyResponse(BaseModel):
    id: int
    family_data: dict

    class Config:
        from_attributes = True


class SubsTypeResponse(BaseModel):
    id: int
    default_subs: Optional[SubsDefaultResponse]
    family_subs: Optional[SubsFamilyResponse]

    class Config:
        from_attributes = True


class SubscriptionResponse(BaseModel):
    id: int
    date_start: date
    date_stop: date
    subscription_type: SubsTypeResponse
    is_test: bool
    # traffic_limit_mb: int

    class Config:
        from_attributes = True


# class CreateFamilyLinkRequest(BaseModel):
#     user_id: str
#     traffic_limit_mb: int
#     name: str


# class CreateFamilyLinkResponse(BaseModel):
#     argument: str


# class ResetFamilySubscriptionRequest(BaseModel):
#     user_id: str
#     name: str
#
#
# class ChangeLocationRequest(BaseModel):
#     new_location: str
#     user_id: str
#
#
# class ProcessFamilyLinkRequest(BaseModel):
#     user_id: str
#     message: str


class ServerResponse(BaseModel):
    location: str
    name: str
    capacity: float


# class ServersResponse(BaseModel):
#     servers: List[ServerResponse]
