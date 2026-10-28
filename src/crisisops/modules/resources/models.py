"""Modelos ORM propiedad de este módulo.

Regla: este archivo no debe importar modelos ORM de otros módulos sin una
decisión arquitectónica común documentada.
"""

from datetime import date

from sqlalchemy import Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from crisisops.core.database import Base


class Resource(Base):
    __tablename__ = 'recursos'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    fecha_ingreso: Mapped[date] = mapped_column(Date, nullable=False)
    estado_recurso: Mapped[str] = mapped_column(String(30), nullable=False)
    peso: Mapped[float] = mapped_column(Float, nullable=False)

class implementos(Base):
    __tablename__ = 'implementos'

    id_recursos: Mapped[int] = mapped_column(Integer, ForeignKey('recursos.id'), primary_key=True)
    tipo_implemento: Mapped[str] = mapped_column(String(100), nullable=False)
    año: Mapped[int] = mapped_column(Integer, nullable=False)
    tipo_uso: Mapped[str] = mapped_column(String(100), nullable=False)
    estado_fisico: Mapped[str] = mapped_column(String(100), nullable=False)

class Vehiculo(Base):
    __tablename__ = 'vehiculos'

    id_recursos: Mapped[int] = mapped_column(Integer, ForeignKey('recursos.id'), primary_key=True)
    patente: Mapped[str] = mapped_column(String(20), nullable=False)
    capacidad: Mapped[int] = mapped_column(Integer, nullable=False)
    modelo: Mapped[str] = mapped_column(String(100), nullable=False)
    tipo_vehiculo: Mapped[str] = mapped_column(String(100), nullable=False)
    año: Mapped[int] = mapped_column(Integer, nullable=False)
    ubicacion: Mapped[str] = mapped_column(String(100), nullable=False)
    ultima_mantencion: Mapped[date] = mapped_column(Date, nullable=False)
    ancho: Mapped[float] = mapped_column(Float, nullable=False)
    largo: Mapped[float] = mapped_column(Float, nullable=False)
    altura: Mapped[float] = mapped_column(Float,nullable=False)
