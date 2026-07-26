from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UploadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    original_filename: str
    stored_filename: str
    folder: str = "general"
    mime_type: str
    size: int
    url: str
    document_type: str | None = None
    document_id: str | None = None
    created_at: datetime
    updated_at: datetime


class UploadUpdate(BaseModel):
    folder: str | None = None
    document_type: str | None = None
    document_id: str | None = None
