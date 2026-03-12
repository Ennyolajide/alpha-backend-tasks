from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, String, Text, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class Briefing(Base):
    __tablename__ = "briefings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    company_name: Mapped[str] = mapped_column(String(255))
    ticker: Mapped[str] = mapped_column(String(20))
    sector: Mapped[str] = mapped_column(String(100))
    analyst_name: Mapped[str] = mapped_column(String(100))
    
    summary: Mapped[str] = mapped_column(Text)
    recommendation: Mapped[str] = mapped_column(Text)
    
    # Defaults to draft; updated once the generation logic finishes
    status: Mapped[str] = mapped_column(String(20), default='draft')
    html_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )

    # Relationship ordering is handled here to keep the API response consistent
    points: Mapped[List["BriefingPoint"]] = relationship(
        "BriefingPoint", 
        back_populates="briefing", 
        cascade="all, delete-orphan", 
        order_by="BriefingPoint.display_order"
    )
    
    risks: Mapped[List["BriefingRisk"]] = relationship(
        "BriefingRisk", 
        back_populates="briefing", 
        cascade="all, delete-orphan", 
        order_by="BriefingRisk.display_order"
    )
    
    metrics: Mapped[List["BriefingMetric"]] = relationship(
        "BriefingMetric", 
        back_populates="briefing", 
        cascade="all, delete-orphan", 
        order_by="BriefingMetric.display_order"
    )


class BriefingPoint(Base):
    __tablename__ = "briefing_points"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    briefing_id: Mapped[int] = mapped_column(ForeignKey("briefings.id", ondelete="CASCADE"))
    content: Mapped[str] = mapped_column(Text)
    display_order: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    briefing: Mapped["Briefing"] = relationship("Briefing", back_populates="points")


class BriefingRisk(Base):
    __tablename__ = "briefing_risks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    briefing_id: Mapped[int] = mapped_column(ForeignKey("briefings.id", ondelete="CASCADE"))
    content: Mapped[str] = mapped_column(Text)
    display_order: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    briefing: Mapped["Briefing"] = relationship("Briefing", back_populates="risks")


class BriefingMetric(Base):
    __tablename__ = "briefing_metrics"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    briefing_id: Mapped[int] = mapped_column(ForeignKey("briefings.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(100))
    value: Mapped[str] = mapped_column(String(100))
    display_order: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    briefing: Mapped["Briefing"] = relationship("Briefing", back_populates="metrics")
    
    # Prevent duplicate metric names (e.g., 'Revenue') within the same report
    __table_args__ = (
        UniqueConstraint("briefing_id", "name", name="uq_briefing_metric_name"),
    )