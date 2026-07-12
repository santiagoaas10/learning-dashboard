"""
Schemas de entrada y salida (la "forma" de los datos en la API).

¿Por qué separar esto del modelo `Course` (la tabla)?
- Lo que el cliente ENVÍA no es igual a lo que se GUARDA ni a lo que se DEVUELVE.
  Ejemplo: al crear un curso el cliente no manda `id` ni `created_at`; esos los
  pone el servidor. Y nunca queremos que el cliente fije el `id` a mano.
- Separar los schemas nos deja validar la entrada y controlar la salida sin
  ensuciar el modelo de la base de datos.

Este es un patrón estándar en APIs serias: modelos de tabla ≠ modelos de I/O.
"""

from datetime import datetime

from pydantic import BaseModel, Field

from app.models import CourseStatus


class CourseCreate(BaseModel):
    """Datos que el cliente envía para CREAR un curso.

    Solo pedimos lo que el usuario decide. El id y las fechas los pone el server.
    Los tipos y las restricciones (`Field`) validan automáticamente: si llega
    algo inválido, FastAPI responde 422 sin que escribamos código extra.
    """

    title: str = Field(min_length=1, description="Nombre del curso (obligatorio)")
    url: str | None = Field(default=None, description="Link al curso")
    platform: str | None = Field(default=None, description="Plataforma, p.ej. Udemy")
    status: CourseStatus = Field(default=CourseStatus.TODO, description="Estado inicial")
    progress: int = Field(default=0, ge=0, le=100, description="Avance 0-100")
    notes: str | None = Field(default=None, description="Notas libres")


class CourseRead(BaseModel):
    """Datos que la API DEVUELVE al cliente.

    Incluye los campos que el servidor genera (id, fechas). Definir la salida
    explícitamente evita filtrar campos internos sin querer.

    `model_config = {"from_attributes": True}` permite construir este schema
    directamente desde un objeto `Course` (leyendo sus atributos), que es justo
    lo que devuelven las consultas a la base de datos.
    """

    id: int
    title: str
    url: str | None
    platform: str | None
    status: CourseStatus
    progress: int
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
