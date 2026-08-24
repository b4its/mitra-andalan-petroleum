from sqlalchemy import String, Text, Enum as SAEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum
import json

from app.models.base import BaseModel


class ActivityType(Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class Activity(BaseModel):
    __tablename__ = "activities"

    user_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="User who performed the action (NULL if system)"
    )
    actor_name: Mapped[str] = mapped_column(String(100), comment="Name of actor/user")
    actor_role: Mapped[str] = mapped_column(String(50), comment="Role of actor")
    action: Mapped[str] = mapped_column(
        SAEnum(
            ActivityType,
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
            named_constructor=True,
        ),
        comment="Action type: create, update, delete"
    )
    resource_type: Mapped[str] = mapped_column(String(100), comment="Resource being acted upon")
    resource_id: Mapped[str | None] = mapped_column(String(36), nullable=True, comment="ID of resource")
    resource_name: Mapped[str | None] = mapped_column(String(200), nullable=True, comment="Display name of resource")
    old_values: Mapped[str | None] = mapped_column(Text, nullable=True, comment="JSON of old values (for update/delete)")
    new_values: Mapped[str | None] = mapped_column(Text, nullable=True, comment="JSON of new values (for create/update)")
    details: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Additional details about the action")
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True, comment="IP address of request")
    user_agent: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="Browser/User Agent info")

    # Relationship
    user = relationship("User", backref="activities", lazy="select")

    @staticmethod
    def serialize_changes(old_data: dict, new_data: dict, action: str) -> tuple[str | None, str | None]:
        """Serialize old and new values to JSON strings with diff tracking"""
        try:
            if action == ActivityType.CREATE.value:
                return None, json.dumps(new_data, indent=2, default=str)
            elif action == ActivityType.UPDATE.value:
                old_json = json.dumps(old_data, indent=2, default=str)
                new_json = json.dumps(new_data, indent=2, default=str)
                return old_json, new_json
            elif action == ActivityType.DELETE.value:
                return json.dumps(old_data, indent=2, default=str), None
            return None, None
        except Exception as e:
            print(f"Error serializing activity changes: {e}")
            return None, None
