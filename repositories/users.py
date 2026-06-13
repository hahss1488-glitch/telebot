from __future__ import annotations
from aiogram.types import User as TgUser
from sqlalchemy import select
from models import User
from .base import BaseRepository

class UserRepository(BaseRepository):
    async def get_or_create(self, tg_user: TgUser) -> User:
        result = await self.session.execute(select(User).where(User.telegram_id == tg_user.id))
        user = result.scalar_one_or_none()
        if user:
            user.username = tg_user.username
            user.first_name = tg_user.first_name
            return user
        user = User(telegram_id=tg_user.id, username=tg_user.username, first_name=tg_user.first_name)
        self.session.add(user)
        await self.session.flush()
        return user
