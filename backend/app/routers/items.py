"""
Rutas del recurso "items" (las tarjetas del tablero).

Un `APIRouter` es como una mini-app: agrupa endpoints relacionados y luego se
"enchufa" a la app principal en main.py con `app.include_router(...)`. Así main
queda limpio y cada recurso vive en su propio archivo.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from app.database import get_session
from app.models import Item, ItemKind, ItemStatus, _now
from app.schemas import ItemCreate, ItemRead, ItemUpdate

# prefix="/items": todas las rutas de aquí empiezan con /items.
# tags=["items"]: agrupa estos endpoints bajo un título en la doc /docs.
router = APIRouter(prefix="/items", tags=["items"])


@router.post("", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
def create_item(
    data: ItemCreate,
    session: Session = Depends(get_session),
) -> Item:
    """Crea un item nuevo.

    - `data: ItemCreate`: FastAPI lee el JSON del body y lo valida contra el
      schema. Si algo no cuadra, responde 422 automáticamente.
    - `session = Depends(get_session)`: FastAPI nos inyecta una sesión de DB.
    - `status_code=201`: convención REST para "recurso creado".
    - `response_model=ItemRead`: la respuesta se filtra a esa forma.
    """
    # Convertimos el schema de entrada en un objeto de tabla `Item`.
    # `model_dump()` pasa los campos validados a un dict; `Item(**dict)` crea la fila.
    item = Item(**data.model_dump())

    session.add(item)      # marca el objeto para insertarse
    session.commit()       # confirma: aquí se escribe de verdad en la DB
    session.refresh(item)  # recarga desde la DB para traer el id y las fechas
    return item


@router.get("", response_model=list[ItemRead])
def list_items(
    # Filtros opcionales que llegan como "query params" en la URL:
    # /items?kind=course&status=in_progress. `Query(default=None)` los hace
    # opcionales; al tiparlos con los Enums, FastAPI valida que el valor sea
    # uno permitido (¿kind=pizza? -> 422 automático).
    kind: ItemKind | None = Query(default=None, description="Filtrar por tipo"),
    item_status: ItemStatus | None = Query(
        default=None,
        alias="status",  # en la URL se llama "status"; en Python evitamos chocar con fastapi.status
        description="Filtrar por columna del tablero",
    ),
    session: Session = Depends(get_session),
) -> list[Item]:
    """Devuelve los items, opcionalmente filtrados por tipo y/o estado.

    La consulta se construye por partes: partimos de "SELECT * FROM item" y
    solo agregamos cada WHERE si el cliente mandó ese filtro.
    """
    query = select(Item)
    if kind is not None:
        query = query.where(Item.kind == kind)
    if item_status is not None:
        query = query.where(Item.status == item_status)

    items = session.exec(query).all()
    return list(items)


def _get_item_or_404(item_id: int, session: Session) -> Item:
    """Busca un item por id o lanza un error 404.

    Lo extraemos en una función porque ver, actualizar y borrar necesitan lo
    mismo: traer el item y, si no existe, responder "404 Not Found". Evita
    repetir el mismo bloque tres veces (principio DRY: Don't Repeat Yourself).

    `session.get(Item, id)` es la forma directa de buscar por clave primaria.
    `HTTPException` hace que FastAPI corte y responda con ese código y mensaje.
    """
    item = session.get(Item, item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe un item con id {item_id}",
        )
    return item


@router.get("/{item_id}", response_model=ItemRead)
def get_item(
    item_id: int,
    session: Session = Depends(get_session),
) -> Item:
    """Devuelve un item puntual por su id (o 404 si no existe).

    `item_id` viene en la URL (p.ej. /items/3). FastAPI lo lee y lo convierte
    a int automáticamente; si no es un número, responde 422.
    """
    return _get_item_or_404(item_id, session)


@router.patch("/{item_id}", response_model=ItemRead)
def update_item(
    item_id: int,
    data: ItemUpdate,
    session: Session = Depends(get_session),
) -> Item:
    """Actualiza parcialmente un item.

    Usamos PATCH (no PUT) porque es una edición PARCIAL: el cliente manda solo
    los campos que cambian. `exclude_unset=True` nos da únicamente esos campos.
    Esto es lo que usará el tablero al arrastrar una tarjeta de columna:
    un PATCH con solo {"status": "in_progress"}.
    """
    item = _get_item_or_404(item_id, session)

    # Solo los campos que el cliente realmente envió.
    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(item, field, value)  # aplica cada cambio al objeto

    item.updated_at = _now()  # dejamos constancia de cuándo se editó

    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: int,
    session: Session = Depends(get_session),
) -> None:
    """Borra un item (o 404 si no existe).

    Responde 204 No Content: la convención REST para "borrado con éxito, no hay
    cuerpo que devolver". Por eso la función no retorna nada.
    """
    item = _get_item_or_404(item_id, session)
    session.delete(item)
    session.commit()
