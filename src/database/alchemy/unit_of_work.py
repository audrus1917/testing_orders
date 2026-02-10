"""The `Unit of Work` :mod:`SQLAlchemy` class."""

from typing import Optional

from src.core.database.unit_of_work import AsyncUnitOfWork


class AlchemyUnitOfWork(AsyncUnitOfWork):

    def __init__(
        self,
        session,
        autocommit: Optional[bool] = False,
    ):
        super(AlchemyUnitOfWork, self).__init__(
            session=session,
            autocommit=autocommit,
        )

    async def begin(self):
        await self.session.begin()

    async def rollback(self):
        await self.session.rollback()

    async def close(self):
        pass

    async def commit(self):
        await self.session.commit()


__all__ = [
    'AlchemyUnitOfWork',
]
