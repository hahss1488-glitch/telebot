from __future__ import annotations
from sqlalchemy import select
from models import ReplacementItem
from .base import BaseRepository

class ReplacementItemRepository(BaseRepository):
    async def list(self, active_only: bool = False) -> list[ReplacementItem]:
        stmt = select(ReplacementItem)
        if active_only: stmt = stmt.where(ReplacementItem.is_active.is_(True))
        res = await self.session.execute(stmt.order_by(ReplacementItem.sort_order, ReplacementItem.name))
        return list(res.scalars())
    async def get(self, item_id: int) -> ReplacementItem | None:
        return await self.session.get(ReplacementItem, item_id)
    async def create(self, name: str, description: str | None = None, sort_order: int = 100) -> ReplacementItem:
        item = ReplacementItem(name=name, description=description, sort_order=sort_order)
        self.session.add(item); await self.session.flush(); return item
    async def seed_defaults(self) -> None:
        if await self.list(): return
        defaults = ["GPS-модуль", "GSM-антенна", "терминал", "релейный модуль", "проводка", "аккумулятор", "предохранитель", "датчик", "замок", "кнопка"]
        for i, name in enumerate(defaults, 10): self.session.add(ReplacementItem(name=name, sort_order=i))
