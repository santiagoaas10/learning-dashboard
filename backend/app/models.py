"""
Modelos de datos.

Un "modelo" con `table=True` en SQLModel cumple dos roles a la vez:
- Define la TABLA en la base de datos (sus columnas y tipos).
- Sirve como objeto Python tipado para trabajar con esas filas.

Aquí vive el modelo central del dashboard: `Item`.

¿Por qué `Item` y no `Course`? Porque en el tablero no solo hay cursos:
también hay proyectos personales, videos de AI por ver y habilidades por
practicar. Todos comparten la misma mecánica (título, estado, prioridad,
fecha límite...), así que usamos UNA tabla con un campo `kind` que dice qué
tipo de cosa es. Esto se llama "generalizar" un modelo: en vez de una tabla
por tipo (4 tablas casi idénticas), una tabla con un discriminador.
"""

from datetime import date, datetime, timezone
from enum import Enum

from sqlmodel import Field, SQLModel


class ItemKind(str, Enum):
    """Qué TIPO de cosa es este item.

    Heredar de `str` además de `Enum` hace que cada valor sea también un string
    normal: se guarda como texto legible en la base de datos y viaja como texto
    en el JSON de la API. Usar un Enum (en vez de un str libre) evita valores
    inválidos: solo estos cuatro son aceptados.
    """

    COURSE = "course"    # un curso por hacer o terminar
    PROJECT = "project"  # un proyecto personal
    VIDEO = "video"      # un video por ver (p.ej. los de AI/Claude)
    SKILL = "skill"      # una habilidad que quiero practicar


class ItemStatus(str, Enum):
    """Columnas del tablero kanban (como en JIRA).

    Agregamos BACKLOG respecto a la v1: es el "cajón de ideas". La diferencia
    con TODO es de compromiso: backlog = "algún día", todo = "es lo siguiente
    que voy a atacar". Separar ambos evita que la columna de pendientes crezca
    infinita y paralice (clave cuando hay MUCHAS cosas empezadas a medias).
    """

    BACKLOG = "backlog"          # ideas / algún día
    TODO = "todo"                # lo siguiente que voy a hacer
    IN_PROGRESS = "in_progress"  # lo estoy haciendo AHORA
    DONE = "done"                # terminado 🎉


class ItemPriority(str, Enum):
    """Prioridad del item, para decidir qué atacar primero."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


def _now() -> datetime:
    """Fecha/hora actual en UTC.

    Guardamos siempre en UTC (hora universal) para evitar líos de zonas
    horarias; la conversión a hora local se hace al mostrar, no al guardar.
    """
    return datetime.now(timezone.utc)


class Item(SQLModel, table=True):
    """Una tarjeta del tablero: curso, proyecto, video o habilidad.

    `table=True` convierte esta clase en una tabla real de la base de datos.
    Cada atributo es una columna; los tipos de Python definen el tipo de columna.
    """

    # Clave primaria. Es `int | None` porque cuando creamos un item en memoria
    # todavía no tiene id: la base de datos lo asigna al guardarlo.
    id: int | None = Field(default=None, primary_key=True)

    # Datos que describe el usuario.
    title: str = Field(index=True)          # indexado: acelera búsquedas por título
    kind: ItemKind = Field(default=ItemKind.COURSE, index=True)  # tipo de item
    url: str | None = Field(default=None)   # link al recurso (opcional)
    platform: str | None = Field(default=None)  # p.ej. "Udemy", "YouTube" (opcional)

    # Organización tipo JIRA.
    status: ItemStatus = Field(default=ItemStatus.BACKLOG, index=True)
    priority: ItemPriority = Field(default=ItemPriority.MEDIUM)
    # `date` (solo día, sin hora): para una meta basta "termino esto el 30 de
    # agosto"; guardar hora exacta sería precisión falsa.
    due_date: date | None = Field(default=None)

    progress: int = Field(default=0)        # porcentaje 0-100 (lo validamos en los schemas)
    notes: str | None = Field(default=None)  # notas libres (opcional)

    # Marcas de tiempo. `default_factory` llama a la función en el momento de
    # crear la fila, así cada item guarda SU propia fecha de creación.
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)
