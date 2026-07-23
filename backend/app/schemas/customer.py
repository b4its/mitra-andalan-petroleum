from pydantic import BaseModel, ConfigDict


class CustomerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    address: str | None = None
    phone: str | None = None
    email: str | None = None


class CustomerCreate(BaseModel):
    name: str
    address: str | None = None
    phone: str | None = None
    email: str | None = None


class CustomerUpdate(BaseModel):
    name: str | None = None
    address: str | None = None
    phone: str | None = None
    email: str | None = None
