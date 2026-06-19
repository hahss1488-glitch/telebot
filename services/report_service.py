from __future__ import annotations
from collections import Counter
from models import ServiceRecord, Vehicle
from repositories.service_records import ServiceRecordRepository

class ReportService:
    def __init__(self, records: ServiceRecordRepository) -> None: self.records = records

    @staticmethod
    def unique_vehicles(rows: list[ServiceRecord]) -> list[Vehicle]:
        vehicles: dict[int, Vehicle] = {}
        for row in rows:
            vehicles.setdefault(row.vehicle_id, row.vehicle)
        return list(vehicles.values())

    @staticmethod
    def _summary_text(title: str, rows: list[ServiceRecord]) -> str:
        vehicles = {r.vehicle_id for r in rows}
        counter = Counter(item.name for r in rows for item in r.items)
        lines = [title, f"Автомобилей: {len(vehicles)}", f"Выполненных задач: {len(rows)}", "", "Статистика задач:"]
        lines += [f"• {name}: {count}" for name, count in counter.most_common()] or ["• нет выбранных задач"]
        return "\n".join(lines)

    async def today(self) -> tuple[str, list[Vehicle]]:
        rows = await self.records.today()
        return self._summary_text("📅 Отчёт за сегодня", rows), self.unique_vehicles(rows)

    async def month(self) -> tuple[str, list[Vehicle]]:
        rows = await self.records.month_to_date()
        return self._summary_text("📊 Отчёт за месяц с 1-го числа", rows), self.unique_vehicles(rows)
