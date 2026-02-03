from typing import Generic, TypeVar, Type, Any, Sequence
from uuid import UUID
from sqlalchemy import select, func, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

ModelType = TypeVar("ModelType", bound=DeclarativeBase)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db


    # create
    async def create(self, **kwargs: Any) -> ModelType:
        instance = self.model(**kwargs)
        self.db.add(instance)
        await self.db.commit()
        await self.db.refresh(instance)
        return instance
    
    async def create_many(self, items: list[dict[str, Any]]) -> list[ModelType]:
        instances = [self.model(**item) for item in items]
        self.db.add_all(instances)
        await self.db.commit()

        for instance in instances:
            await self.db.refresh(instance)

        return instances
    

    # read
    async def get_by_id(self, id: UUID) -> ModelType | None:
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_field(
        self,
        field_name: str,
        field_value: Any
    ) -> ModelType | None:
        result = await self.db.execute(
            select(self.model).where(
                getattr(self.model, field_name) == field_value
            )
        )
        return result.scalar_one_or_none()
    
    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[ModelType]:
        result = await self.db.execute(
            select(self.model)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def list_by_field(
        self,
        field_name: str,
        field_value: Any,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[ModelType]:
        result = await self.db.execute(
            select(self.model)
            .where(getattr(self.model, field_name) == field_value)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def count(self) -> int:
        result = await self.db.execute(
            select(func.count()).select_from(self.model)
        )
        return result.scalar_one()
    
    async def count_by_field(
        self,
        field_name: str,
        field_value: Any
    ) -> int:
        result = await self.db.execute(
            select(func.count())
            .select_from(self.model)
            .where(getattr(self.model, field_name) == field_value)
        )
        return result.scalar_one()
    
    async def exists(self, id: UUID) -> bool:
        result = await self.db.execute(
            select(func.count())
            .select_from(self.model)
            .where(self.model.id == id)
        )
        count = result.scalar_one()
        return count > 0
    
    async def exists_by_field(
        self,
        field_name: str,
        field_value: Any
    ) -> bool:
        result = await self.db.execute(
            select(func.count())
            .select_from(self.model)
            .where(getattr(self.model, field_name) == field_value)
        )
        count = result.scalar_one()
        return count > 0
    

    # update
    async def update_instance(self, instance: ModelType) -> ModelType:
        self.db.add(instance)
        await self.db.commit()
        await self.db.refresh(instance)
        return instance
    
    async def update_by_id(
        self,
        id: UUID,
        **kwargs: Any
    ) -> ModelType | None:
        await self.db.execute(
            update(self.model)
            .where(self.model.id == id)
            .values(**kwargs)
        )
        await self.db.commit()

        return await self.get_by_id(id)
    
    
    # delete
    async def delete_by_id(self, id: UUID) -> bool:
        result = await self.db.execute(
            delete(self.model).where(self.model.id == id)
        )
        await self.db.commit()

        return result.rowcount > 0
    
    async def delete_instance(self, instance: ModelType) -> None:
        self.db.delete(instance)
        await self.db.commit()

    async def soft_delete_by_id(self, id: UUID) -> bool:
        from datetime import datetime, timezone

        if not hasattr(self.model, "deleted_at"):
            raise AttributeError(
                f"{self.model.__name__} não tem soft delete (deleted_at)"
            )
        
        result = await self.db.execute(
            update(self.model)
            .where(self.model.id == id)
            .values(deleted_at=datetime.now(timezone.utc))
        )
        await self.db.commit()
        
        return result.rowcount > 0
    

    # utility methods
    async def refresh(self, instance: ModelType) -> ModelType:
        await self.db.refresh(instance)
        return instance
    
    async def commit(self) -> None:
        await self.db.commit()

    async def rollback(self) -> None:
        await self.db.rollback()