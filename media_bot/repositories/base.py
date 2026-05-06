from sqlalchemy import select, update, delete, func
from media_bot.services.database import AsyncSessionLocal, User, Media
from datetime import datetime
from typing import List, Optional

class UserRepository:
    @staticmethod
    async def get_or_create(user_id: int, **kwargs) -> User:
        async with AsyncSessionLocal() as session:
            user = await session.get(User, user_id)
            if not user:
                user = User(id=user_id, **kwargs)
                session.add(user)
                await session.commit()
            else:
                user.last_active = datetime.utcnow()
                for key, value in kwargs.items():
                    setattr(user, key, value)
                await session.commit()
            return user

    @staticmethod
    async def is_blocked(user_id: int) -> bool:
        async with AsyncSessionLocal() as session:
            user = await session.get(User, user_id)
            return user.is_blocked if user else False

class MediaRepository:
    @staticmethod
    async def save(media_data: dict) -> Media:
        async with AsyncSessionLocal() as session:
            media = Media(**media_data)
            session.add(media)
            await session.commit()
            await session.refresh(media)
            return media

    @staticmethod
    async def find_by_hash(file_hash: str) -> Optional[Media]:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Media).where(Media.file_hash == file_hash))
            return result.scalar_one_or_none()

    @staticmethod
    async def get_recent(user_id: int, limit: int = 10) -> List[Media]:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Media).where(Media.user_id == user_id)
                .order_by(Media.created_at.desc())
                .limit(limit)
            )
            return result.scalars().all()
