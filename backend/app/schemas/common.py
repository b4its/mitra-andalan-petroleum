from datetime import datetime
from typing import Annotated, Generic, TypeVar

from pydantic import BaseModel, BeforeValidator, ConfigDict

T = TypeVar("T")


def _empty_str_to_none(v):
    if isinstance(v, str) and not v.strip():
        return None
    return v


ForeignKeyId = Annotated[str | None, BeforeValidator(_empty_str_to_none)]


class TimestampMixin(BaseModel):
    created_at: datetime
    updated_at: datetime


class BaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime


class MessageResponse(BaseModel):
    message: str
    code: int = 200


class PaginationParams(BaseModel):
    page: int = 1
    page_size: int = 10


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    pages: int = 0
