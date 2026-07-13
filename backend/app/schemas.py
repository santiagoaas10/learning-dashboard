"""
Schemas de entrada y salida (la "forma" de los datos en la API).

¿Por qué separar esto del modelo `Item` (la tabla)?
- Lo que el cliente ENVÍA no es igual a lo que se GUARDA ni a lo que se DEVUELVE.
  Ejemplo: al crear un item el cliente no manda `id` ni `created_at`; esos los
  pone el servidor. Y nunca queremos que el cliente fije el `id` a mano.
- Separar los schemas nos deja validar la entrada y controlar la salida sin
  ensuciar el modelo de la base de datos.

Este es un patrón estándar en APIs serias: modelos de tabla ≠ modelos de I/O.
"""

from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field

from app.models import ItemKind, ItemPriority, ItemStatus


# --- Auth ---

class UserCreate(BaseModel):
    """Datos para registrarse o iniciar sesión (email + contraseña).

    `EmailStr` valida el formato del email automáticamente (necesita el
    paquete email-validator). El mínimo de 8 caracteres es una defensa básica
    contra contraseñas triviales.
    """

    email: EmailStr
    password: str = Field(min_length=8)


class UserRead(BaseModel):
    """Lo que devolvemos de un usuario. Nótese lo que NO está: el hash de la
    contraseña jamás sale de la API."""

    id: int
    email: EmailStr

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """Respuesta del login/registro: el token de sesión.

    `token_type: "bearer"` le indica al cliente cómo usarlo: en el header
    `Authorization: Bearer <access_token>`. Es la convención OAuth2.
    """

    access_token: str
    token_type: str = "bearer"


class ItemCreate(BaseModel):
    """Datos que el cliente envía para CREAR un item.

    Solo pedimos lo que el usuario decide. El id y las fechas de auditoría los
    pone el server. Los tipos y las restricciones (`Field`) validan
    automáticamente: si llega algo inválido, FastAPI responde 422 sin que
    escribamos código extra.
    """

    title: str = Field(min_length=1, description="Nombre del item (obligatorio)")
    kind: ItemKind = Field(default=ItemKind.COURSE, description="Tipo: course/project/video/skill")
    url: str | None = Field(default=None, description="Link al recurso")
    platform: str | None = Field(default=None, description="Plataforma, p.ej. Udemy")
    status: ItemStatus = Field(default=ItemStatus.BACKLOG, description="Columna inicial del tablero")
    priority: ItemPriority = Field(default=ItemPriority.MEDIUM, description="Prioridad")
    due_date: date | None = Field(default=None, description="Fecha límite (solo día)")
    progress: int = Field(default=0, ge=0, le=100, description="Avance 0-100")
    notes: str | None = Field(default=None, description="Notas libres")


class ItemUpdate(BaseModel):
    """Datos para ACTUALIZAR un item (edición parcial).

    Todos los campos son opcionales: el cliente manda solo lo que quiere cambiar.
    Por eso cada campo tiene `default=None`. Al aplicar la actualización usamos
    `exclude_unset=True` para distinguir "no lo mandó" de "lo mandó en null", y
    así tocar únicamente los campos enviados.
    """

    title: str | None = Field(default=None, min_length=1)
    kind: ItemKind | None = None
    url: str | None = None
    platform: str | None = None
    status: ItemStatus | None = None
    priority: ItemPriority | None = None
    due_date: date | None = None
    progress: int | None = Field(default=None, ge=0, le=100)
    notes: str | None = None


class ItemRead(BaseModel):
    """Datos que la API DEVUELVE al cliente.

    Incluye los campos que el servidor genera (id, fechas). Definir la salida
    explícitamente evita filtrar campos internos sin querer.

    `model_config = {"from_attributes": True}` permite construir este schema
    directamente desde un objeto `Item` (leyendo sus atributos), que es justo
    lo que devuelven las consultas a la base de datos.
    """

    id: int
    title: str
    kind: ItemKind
    url: str | None
    platform: str | None
    status: ItemStatus
    priority: ItemPriority
    due_date: date | None
    progress: int
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
