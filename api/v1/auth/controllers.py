from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.auth.schemas import UserSchema
from core.database import User


async def get_user(session: AsyncSession, user_id: int) -> User:
    stmt = select(User).where(User.id == user_id)
    return await session.scalar(stmt)


async def create_user(session: AsyncSession, user_in: UserSchema) -> User:
    user = User(**user_in.model_dump())
    session.add(user)
    await session.commit()
    return user


async def get_user_by_username(session: AsyncSession, username: str) -> User:
    stmt = select(User).where(User.username == username)
    return await session.scalar(stmt)
