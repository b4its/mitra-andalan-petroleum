from pydantic import BaseModel, ConfigDict, EmailStr


class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    email: str
    role: str


class ProfileCreate(BaseModel):
    name: str
    email: str
    password: str
    role: str = "staff"


class ProfileUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    password: str | None = None
    role: str | None = None
