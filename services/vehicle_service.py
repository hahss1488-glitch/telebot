from __future__ import annotations
import logging
from models import Vehicle
from repositories.vehicles import VehicleRepository
from utils.plate import normalize_plate, normalize_region
logger = logging.getLogger(__name__)

class VehicleService:
    def __init__(self, repo: VehicleRepository) -> None: self.repo = repo
    async def get_or_create(self, plate: str, region: str) -> tuple[Vehicle, bool]:
        plate_n, region_n = normalize_plate(plate), normalize_region(region)
        vehicle = await self.repo.get_by_plate_region(plate_n, region_n)
        if vehicle: return vehicle, False
        vehicle = await self.repo.create(plate_n, region_n)
        logger.info("Vehicle created: %s %s", plate_n, region_n)
        return vehicle, True
    async def set_note(self, vehicle: Vehicle, note: str | None) -> Vehicle:
        vehicle.note = note; return vehicle
