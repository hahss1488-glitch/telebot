from __future__ import annotations

from datetime import datetime
from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    username: Mapped[str | None] = mapped_column(String(255))
    first_name: Mapped[str | None] = mapped_column(String(255))
    registered_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

class Vehicle(Base):
    __tablename__ = "vehicles"
    __table_args__ = (
        UniqueConstraint("plate_number", "region", name="uq_vehicle_plate_region"),
        Index("ix_vehicle_plate_region", "plate_number", "region"),
        Index("ix_vehicle_note", "note"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    plate_number: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    region: Mapped[str] = mapped_column(String(8), index=True, nullable=False)
    note: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(16), default="normal", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    service_records: Mapped[list[ServiceRecord]] = relationship(back_populates="vehicle", cascade="all, delete-orphan")

class ServiceRecord(Base):
    __tablename__ = "service_records"
    __table_args__ = (Index("ix_service_vehicle_date", "vehicle_id", "service_date"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id", ondelete="CASCADE"), index=True, nullable=False)
    performer_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    service_date: Mapped[datetime] = mapped_column(DateTime, index=True, nullable=False, default=datetime.utcnow)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text)
    vehicle: Mapped[Vehicle] = relationship(back_populates="service_records")
    performer: Mapped[User | None] = relationship()
    items: Mapped[list[ReplacementItem]] = relationship(secondary="service_record_items", back_populates="service_records")

class ReplacementItem(Base):
    __tablename__ = "replacement_items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    service_records: Mapped[list[ServiceRecord]] = relationship(secondary="service_record_items", back_populates="items")

class ServiceRecordItem(Base):
    __tablename__ = "service_record_items"
    service_record_id: Mapped[int] = mapped_column(ForeignKey("service_records.id", ondelete="CASCADE"), primary_key=True)
    replacement_item_id: Mapped[int] = mapped_column(ForeignKey("replacement_items.id", ondelete="RESTRICT"), primary_key=True)
