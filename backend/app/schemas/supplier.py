from pydantic import BaseModel, ConfigDict


class SupplierResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    address: str | None = None
    phone: str | None = None
    email: str | None = None


class SupplierCreate(BaseModel):
    name: str
    address: str | None = None
    phone: str | None = None
    email: str | None = None


class SupplierUpdate(BaseModel):
    name: str | None = None
    address: str | None = None
    phone: str | None = None
    email: str | None = None
