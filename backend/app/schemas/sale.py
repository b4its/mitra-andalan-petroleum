from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SaleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    date: str
    status: str
    email: str
    amount: float
    created_at: datetime


class SaleCreate(BaseModel):
    date: str
    status: str
    email: str
    amount: float


class SaleUpdate(BaseModel):
    date: str | None = None
    status: str | None = None
    email: str | None = None
    amount: float | None = None
