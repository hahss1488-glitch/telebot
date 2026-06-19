from __future__ import annotations
from sqlalchemy import func, or_, select
from sqlalchemy.orm import selectinload
from models import Vehicle
from .base import BaseRepository

class VehicleRepository(BaseRepository):
    async def get(self, vehicle_id: int) -> Vehicle | None:
        return await self.session.get(Vehicle, vehicle_id, options=[selectinload(Vehicle.service_records)])
    async def get_by_plate_region(self, plate: str, region: str) -> Vehicle | None:
        res = await self.session.execute(select(Vehicle).where(Vehicle.plate_number == plate, Vehicle.region == region))
        return res.scalar_one_or_none()
    async def create(self, plate: str, region: str, note: str | None = None) -> Vehicle:
        vehicle = Vehicle(plate_number=plate, region=region, note=note, status="normal")
        self.session.add(vehicle); await self.session.flush(); return vehicle
    async def search(self, query: str, limit: int = 20) -> list[Vehicle]:
        like = f"%{query}%"
        full_number = Vehicle.plate_number + Vehicle.region
        res = await self.session.execute(select(Vehicle).where(or_(Vehicle.plate_number.like(like), Vehicle.region.like(like), full_number.like(like), Vehicle.note.like(like))).order_by(Vehicle.updated_at.desc()).limit(limit))
        return list(res.scalars())
    async def problematic(self, limit: int = 50) -> list[Vehicle]:
        res = await self.session.execute(select(Vehicle).where(Vehicle.status == "problem").order_by(Vehicle.updated_at.desc()).limit(limit))
        return list(res.scalars())
    async def count(self) -> int:
        res = await self.session.execute(select(func.count(Vehicle.id)))
        return int(res.scalar() or 0)
    async def delete(self, vehicle: Vehicle) -> None:
        await self.session.delete(vehicle)
