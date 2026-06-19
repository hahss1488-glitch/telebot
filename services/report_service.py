from __future__ import annotations
from collections import Counter
from repositories.service_records import ServiceRecordRepository

class ReportService:
    def __init__(self, records: ServiceRecordRepository) -> None: self.records = records
    async def today_text(self) -> str:
        rows = await self.records.today()
        vehicles = {r.vehicle_id for r in rows}
        counter = Counter(item.name for r in rows for item in r.items)
        lines = ["Отчёт за сегодня", f"Автомобилей: {len(vehicles)}", f"Выполненных задач: {len(rows)}", "", "Замены:"]
        lines += [f"• {name}: {count}" for name, count in counter.most_common()] or ["• нет"]
        lines += ["", "Последние записи:"]
        lines += [f"• {r.service_date:%H:%M} {r.vehicle.plate_number}{r.vehicle.region}: {r.description[:80]}" for r in rows[:10]] or ["• нет"]
        return "\n".join(lines)
    async def month_text(self) -> str:
        rows = await self.records.month_to_date()
        vehicles = {r.vehicle_id for r in rows}
        counter = Counter(item.name for r in rows for item in r.items)
        lines = ["Отчёт за месяц с 1-го числа", f"Автомобилей: {len(vehicles)}", f"Выполненных задач: {len(rows)}", "", "Статистика задач:"]
        lines += [f"• {name}: {count}" for name, count in counter.most_common()] or ["• нет замен"]
        return "\n".join(lines)
