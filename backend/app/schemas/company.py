from pydantic import BaseModel, Field


class CompanyResponse(BaseModel):
    id: str
    name: str
    abbreviation: str
    company_image: str | None = None


class CompanyCreate(BaseModel):
    name: str
    abbreviation: str = Field(max_length=20)
    company_image: str | None = None


class CompanyUpdate(BaseModel):
    name: str | None = None
    abbreviation: str | None = Field(default=None, max_length=20)
    company_image: str | None = None
