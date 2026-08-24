from pydantic import BaseModel, ConfigDict

class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    email: str
    role: str
    signature: str | None = None
    signature_caption: str | None = None

class ProfileDemoResponse(ProfileResponse):
    password: str

class ProfileCreate(BaseModel):
    name: str
    email: str
    password: str
    role: str = "staff"
    signature: str | None = None
    signature_caption: str | None = None

class ProfileUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    password: str | None = None
    role: str | None = None
    signature: str | None = None
    signature_caption: str | None = None
