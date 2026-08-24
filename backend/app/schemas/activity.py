from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ActivityResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    actor_name: str
    actor_role: str
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    resource_name: Optional[str] = None
    old_values: Optional[str] = None
    new_values: Optional[str] = None
    details: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime
    
    model_config = {"from_attributes": True}


class ActivityFilter(BaseModel):
    action: Optional[str] = None
    resource_type: Optional[str] = None
    actor_name: Optional[str] = None
    user_id: Optional[str] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
