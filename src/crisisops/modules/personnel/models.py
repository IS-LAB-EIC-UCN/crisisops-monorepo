"""Modelos ORM propiedad de este módulo.

Regla: este archivo no debe importar modelos ORM de otros módulos sin una
decisión arquitectónica común documentada.
"""
from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, Enum, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from crisisops.core.database import Base


class Responder(Base):
    __tablename__ = "responders"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    badge_number: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    skills: Mapped[list[ResponderSkill]] = relationship(back_populates="responder")
    certifications: Mapped[list[Certification]] = relationship(back_populates="responder")
    shifts: Mapped[list[Shift]] = relationship(back_populates="responder")
    assignments: Mapped[list[PersonnelAssignment]] = relationship(back_populates="responder")


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    requires_certification: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class ResponderSkill(Base):
    __tablename__ = "responder_skills"
    __table_args__ = (UniqueConstraint("responder_id", "skill_code"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    responder_id: Mapped[int] = mapped_column(ForeignKey("responders.id"), nullable=False)
    skill_code: Mapped[str] = mapped_column(ForeignKey("skills.code"), nullable=False)

    responder: Mapped[Responder] = relationship(back_populates="skills")


class Certification(Base):
    __tablename__ = "certifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    responder_id: Mapped[int] = mapped_column(ForeignKey("responders.id"), nullable=False)
    skill_code: Mapped[str] = mapped_column(ForeignKey("skills.code"), nullable=False)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    responder: Mapped[Responder] = relationship(back_populates="certifications")

    def is_valid_for(self, moment: datetime) -> bool:
        return self.issued_at <= moment < self.expires_at


class Shift(Base):
    __tablename__ = "shifts"

    id: Mapped[int] = mapped_column(primary_key=True)
    responder_id: Mapped[int] = mapped_column(ForeignKey("responders.id"), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    responder: Mapped[Responder] = relationship(back_populates="shifts")

    def covers(self, start: datetime, end: datetime) -> bool:
        return self.start_time <= start and self.end_time >= end


class AssignmentStatus(enum.StrEnum):
    RESERVED = "RESERVED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class PersonnelAssignment(Base):
    __tablename__ = "personnel_assignments"
    __table_args__ = (
        CheckConstraint("start_at < end_at", name="ck_assignment_start_before_end"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    responder_id: Mapped[int] = mapped_column(ForeignKey("responders.id"), nullable=False, index=True)
    mission_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[AssignmentStatus] = mapped_column(Enum(AssignmentStatus), nullable=False, default=AssignmentStatus.ACTIVE)

    responder: Mapped[Responder] = relationship(back_populates="assignments")

    def overlaps(self, start: datetime, end: datetime) -> bool:
        if start >= end:
            raise ValueError("start debe ser anterior a end")
        return self.start_at < end and start < self.end_at
