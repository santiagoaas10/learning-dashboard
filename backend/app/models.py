"""
Modelos de datos.

Un "modelo" con `table=True` en SQLModel cumple dos roles a la vez:
- Define la TABLA en la base de datos (sus columnas y tipos).
- Sirve como objeto Python tipado para trabajar con esas filas.

Aquí vive el modelo central de la v1: `Course` (un curso que quiero hacer).
"""

from datetime import datetime, timezone
from enum import Enum

from sqlmodel import Field, SQLModel


class CourseStatus(str, Enum):
    """Estados posibles de un curso.

    Heredar de `str` además de `Enum` hace que cada valor sea también un string
    normal ("todo", "in_progress"...). Así se guarda como texto legible en la
    base de datos y viaja como texto en el JSON de la API.

    Usar un Enum (en vez de un str libre) evita estados inválidos: solo estos
    tres valores son aceptados.
    """

    TODO = "todo"                # aún no lo empiezo
    IN_PROGRESS = "in_progress"  # lo estoy haciendo
    DONE = "done"                # lo terminé


def _now() -> datetime:
    """Fecha/hora actual en UTC.

    Guardamos siempre en UTC (hora universal) para evitar líos de zonas
    horarias; la conversión a hora local se hace al mostrar, no al guardar.
    """
    return datetime.now(timezone.utc)


class Course(SQLModel, table=True):
    """Un curso que quiero hacer.

    `table=True` convierte esta clase en una tabla real de la base de datos.
    Cada atributo es una columna; los tipos de Python definen el tipo de columna.
    """

    # Clave primaria. Es `int | None` porque cuando creamos un curso en memoria
    # todavía no tiene id: la base de datos lo asigna al guardarlo.
    id: int | None = Field(default=None, primary_key=True)

    # Datos que describe el usuario.
    title: str = Field(index=True)          # indexado: acelera búsquedas por título
    url: str | None = Field(default=None)   # link al curso (opcional)
    platform: str | None = Field(default=None)  # p.ej. "Udemy", "YouTube" (opcional)

    # Estado y avance.
    status: CourseStatus = Field(default=CourseStatus.TODO)
    progress: int = Field(default=0)        # porcentaje 0-100 (lo validamos en los schemas)

    notes: str | None = Field(default=None)  # notas libres (opcional)

    # Marcas de tiempo. `default_factory` llama a la función en el momento de
    # crear la fila, así cada curso guarda SU propia fecha de creación.
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)
