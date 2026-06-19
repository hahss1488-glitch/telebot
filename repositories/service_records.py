from __future__ import annotations
from datetime import datetime, time
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from models import ReplacementItem, ServiceRecord
from .base import BaseRepository

class ServiceRecordRepository(BaseRepository):
    async def create(self, vehicle_id: int, performer_id: int | None, description: str, item_ids: set[int], comment: str | None = None) -> ServiceRecord:
        record = ServiceRecord(vehicle_id=vehicle_id, performer_id=performer_id, description=description, comment=comment, service_date=datetime.utcnow())
        if item_ids:
            items = await self.session.execute(select(ReplacementItem).where(ReplacementItem.id.in_(item_ids)))
            record.items = list(items.scalars())
        self.session.add(record); await self.session.flush(); return record
    async def get(self, record_id: int) -> ServiceRecord | None:
        return await self.session.get(ServiceRecord, record_id, options=[selectinload(ServiceRecord.items), selectinload(ServiceRecord.performer), selectinload(ServiceRecord.vehicle)])
    async def history(self, vehicle_id: int, offset: int = 0, limit: int = 5) -> list[ServiceRecord]:
        res = await self.session.execute(select(ServiceRecord).where(ServiceRecord.vehicle_id == vehicle_id).options(selectinload(ServiceRecord.items), selectinload(ServiceRecord.performer)).order_by(ServiceRecord.service_date.desc()).offset(offset).limit(limit))
        return list(res.scalars())
    async def today(self) -> list[ServiceRecord]:
        start = datetime.combine(datetime.utcnow().date(), time.min)
        res = await self.session.execute(select(ServiceRecord).where(ServiceRecord.service_date >= start).options(selectinload(ServiceRecord.items), selectinload(ServiceRecord.vehicle), selectinload(ServiceRecord.performer)).order_by(ServiceRecord.service_date.desc()))
        return list(res.scalars())
    async def month_to_date(self) -> list[ServiceRecord]:
        now = datetime.utcnow(); start = datetime(now.year, now.month, 1)
        res = await self.session.execute(select(ServiceRecord).where(ServiceRecord.service_date >= start).options(selectinload(ServiceRecord.items), selectinload(ServiceRecord.vehicle)).order_by(ServiceRecord.service_date.desc()))
        return list(res.scalars())
    async def count_for_vehicle(self, vehicle_id: int) -> int:
        res = await self.session.execute(select(func.count(ServiceRecord.id)).where(ServiceRecord.vehicle_id == vehicle_id))
        return int(res.scalar() or 0)
