from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.activity import Activity, ActivityType


async def log_activity(
    db: AsyncSession,
    request: Request | None = None,
    user_id: str | None = None,
    actor_name: str = "System",
    actor_role: str = "system",
    action: str = "unknown",
    resource_type: str = "",
    resource_id: str | None = None,
    resource_name: str | None = None,
    old_data: dict | None = None,
    new_data: dict | None = None,
    details: str | None = None
):
    """
    Log any activity in the system with full audit trail
    
    Args:
        db: Database session
        request: Optional FastAPI request for IP/User-Agent
        user_id: ID of user performing action
        actor_name: Name of user/system performing action
        actor_role: Role of actor (admin, marketing, etc)
        action: Type of action (create, update, delete)
        resource_type: Type of resource being acted upon
        resource_id: ID of resource
        resource_name: Display name of resource
        old_data: Dictionary of old values (for update/delete)
        new_data: Dictionary of new values (for create/update)
        details: Additional details about the action
    """
    
    # Get IP and User-Agent from request
    ip_address = None
    user_agent = None
    
    if request:
        # Handle both proxy and direct requests
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            ip_address = forwarded_for.split(",")[0].strip()
        else:
            ip_address = request.client.host if request.client else None
        
        user_agent = request.headers.get("user-agent")
    
    # Serialize old and new data
    old_values, new_values = Activity.serialize_changes(
        old_data or {}, 
        new_data or {}, 
        action
    )
    
    # Create activity record
    activity = Activity(
        user_id=user_id,
        actor_name=actor_name,
        actor_role=actor_role,
        action=ActivityType(action),
        resource_type=resource_type,
        resource_id=resource_id,
        resource_name=resource_name,
        old_values=old_values,
        new_values=new_values,
        details=details,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    db.add(activity)
    await db.flush()
    
    return activity
