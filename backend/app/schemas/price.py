from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PriceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    category: str
    name: str
    price: float
    unit: str
    notes: str | None = None
    effective_date: str | None = None
    created_at: datetime


class PriceCreate(BaseModel):
    category: str = Field(min_length=1, max_length=30)
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(ge=0)
    unit: str = Field(default="", max_length=30)
    notes: str | None = Field(default=None, max_length=255)
    effective_date: str | None = Field(default=None, max_length=20)


class PriceUpdate(BaseModel):
    category: str | None = Field(default=None, min_length=1, max_length=30)
    name: str | None = Field(default=None, min_length=1, max_length=100)
    price: float | None = Field(default=None, ge=0)
    unit: str | None = Field(default=None, max_length=30)
    notes: str | None = Field(default=None, max_length=255)
    effective_date: str | None = Field(default=None, max_length=20)
