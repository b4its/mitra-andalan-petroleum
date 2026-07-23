from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    name: str
    email: str
    role: str
    token: str
    logged_in_at: str
