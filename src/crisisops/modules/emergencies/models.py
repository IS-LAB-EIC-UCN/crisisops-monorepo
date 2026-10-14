"""Modelos ORM propiedad de este módulo.

Regla: este archivo no debe importar modelos ORM de otros módulos sin una
decisión arquitectónica común documentada.
"""

from datetime import UTC, datetime
from sqlalchemy import DateTime, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from crisisops.core.database import Base
from crisisops.modules.emergencies.enums import EmergencyStatus, EmergencyType

def _utcnow() -> datetime:
    return datetime.now(UTC)

'''
SAEnum convierte entre el valor del enum en python y el texto guardado en la base de datos, 
asi al leer se obtiene el enum y no un String suelto.
SAENum también se encarga de convertir los valores recuperador de la base de datos 
al tipo definido en /models/emergency/enums.
native_enum=False guarda el valr como Varchar en vez de usar el tipo ENUM de POstgreSQL.
'''
def _enum_column(enum_cls: type, length: int):
    return SAEnum(enum_cls, native_enum=False, 
    length=length, validate_strings=True)

class Emergency(Base):
    __tablename__ = "emergencies"

    id: Mapped[int] = mapped_column(primary_key=True)
    #Tipo de emergencia, con valores estandarizados en EmergencyType

    title: Mapped[str] = mapped_column(String(60), nullable=True)
    
    type: Mapped[EmergencyType] = mapped_column(_enum_column(EmergencyType,30), nullable=False)
    #detalles del tipo de emergencia, en el caso que el type anterior sea "OTHER", por lo que se debe indicar que tipo de emergencia es.
    type_detail: Mapped[str|None] = mapped_column(String(200), nullable=True)
    #Descripción detallada de la emergencia
    description : Mapped[str] = mapped_column(Text, nullable=True)
    #Locación de la emergencia
    location_description: Mapped[str] = mapped_column(String(250), nullable=True)
    #Status de la emergencia, los valores que pueden tomar estan estandarizados en la clase EmergencyStatus
    status: Mapped[EmergencyStatus] = mapped_column(_enum_column(EmergencyStatus, 20), nullable=False, default=EmergencyStatus.REPORTED)
    #Quien es el que reporta. Sirve para la trazabilidad. como la creación de una tabla Usuarios requiere la coordinación de los demas modulos, por ahora utilizamos reported_by (un string).
    reported_by: Mapped[str] = mapped_column(String(120), nullable=False)
    #Fecha de creación para llevar trazabilidad.
    created_at: Mapped[datetime] =  mapped_column(DateTime(timezone=True), default=_utcnow, nullable=False)
    #Fecha que indica la ultima actualización
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate = _utcnow, nullable=False)