from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    message: str
    type: str = "info"
    sender_id: str | None = None
    user_name: str | None = None
    to: str | None = None
    is_read: bool = False
    created_at: datetime


class NotificationCreate(BaseModel):
    title: str
    message: str
    type: str = "info"
    sender_id: str | None = None
    to: str | None = None
    is_read: bool = False


class NotificationUpdate(BaseModel):
    title: str | None = None
    message: str | None = None
    type: str | None = None
    sender_id: str | None = None
    to: str | None = None
    is_read: bool | None = None
