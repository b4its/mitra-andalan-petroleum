from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class BaseService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, model, id: str):
        stmt = select(model).where(model.id == id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(self, model, skip: int = 0, limit: int = 100):
        stmt = select(model).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create(self, instance):
        self.db.add(instance)
        await self.db.flush()
        await self.db.refresh(instance)
        return instance

    async def delete(self, instance):
        await self.db.delete(instance)
        await self.db.flush()
