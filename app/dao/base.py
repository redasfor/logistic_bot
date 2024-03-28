from sqlalchemy import select, insert, delete, and_, func
from app.database import async_session_maker


class BaseDAO:
    model = None

    @classmethod
    async def delete_by_names(cls, **kwargs):
        async with async_session_maker() as session:
            # Построение запроса на удаление с проверкой условий
            query = delete(cls.model).where(
                and_(*[getattr(cls.model, key) == value for key, value in kwargs.items()])
            )
            result = await session.execute(query)
            # Проверяем, были ли затронуты строки
            if result.rowcount > 0:
                await session.commit()
                return True  # Удаление было успешно
            else:
                # Не было найдено записей для удаления
                return False

    @classmethod
    async def find_by_id(cls, model_id: int):
        async with async_session_maker() as session:
            query = select(cls.model.__table__.columns).filter_by(id=model_id)
            result = await session.execute(query)
            return result.mappings().one_or_none()

    @classmethod
    async def find_all(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model.__table__.columns).filter_by(**filter_by)
            result = await session.execute(query)
            return result.mappings().all()

    @classmethod
    async def find_one_or_none(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model.__table__.columns).filter_by(**filter_by)
            result = await session.execute(query)
            return result.mappings().one_or_none()

    @classmethod
    async def add(cls, **data):
        async with async_session_maker() as session:
            query = insert(cls.model).values(**data)
            await session.execute(query)
            await session.commit()

    @classmethod
    async def total_rows(cls):
        async with async_session_maker() as session:
            query = select(cls.model.__table__.columns)
            result = await session.execute(query)
            return len(result.mappings().all())

    @classmethod
    async def count_users_with_templates(cls):
        async with async_session_maker() as session:
            query = select(func.count(func.distinct(cls.model.user_id)))
            result = await session.execute(query)
            return result.scalar()

    @classmethod
    async def max_time(cls):
        async with async_session_maker() as session:
            query = func.max(cls.model.date)
            result = await session.execute(query)
            return result.mappings().one()
