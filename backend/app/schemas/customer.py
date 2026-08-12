from pydantic import BaseModel, ConfigDict, Field


class CustomerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    npwp: str | None = None
    address: str | None = None
    province: str | None = None
    city: str | None = None
    phone: str | None = None
    phone2: str | None = None
    email: str | None = None


class CustomerCreate(BaseModel):
    name: str
    npwp: str | None = Field(default=None, max_length=20)
    address: str | None = None
    province: str | None = None
    city: str | None = None
    phone: str | None = None
    phone2: str | None = None
    email: str | None = None


class CustomerUpdate(BaseModel):
    name: str | None = None
    npwp: str | None = Field(default=None, max_length=20)
    address: str | None = None
    province: str | None = None
    city: str | None = None
    phone: str | None = None
    phone2: str | None = None
    email: str | None = None
