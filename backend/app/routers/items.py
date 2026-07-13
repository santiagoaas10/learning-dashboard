"""
Rutas del recurso "items" (las tarjetas del tablero).

Un `APIRouter` es como una mini-app: agrupa endpoints relacionados y luego se
"enchufa" a la app principal en main.py con `app.include_router(...)`. Así main
queda limpio y cada recurso vive en su propio archivo.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from app.database import get_session
from app.models import Item, ItemKind, ItemStatus, User, _now
from app.schemas import ItemCreate, ItemRead, ItemUpdate
from app.security import get_current_user

# prefix="/items": todas las rutas de aquí empiezan con /items.
# tags=["items"]: agrupa estos endpoints bajo un título en la doc /docs.
#
# Todos los endpoints declaran `user: User = Depends(get_current_user)`:
# sin token válido responden 401, y con token cada consulta se limita a los
# items de ESE usuario. Nadie puede ver ni tocar tarjetas ajenas.
router = APIRouter(prefix="/items", tags=["items"])


@router.post("", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
def create_item(
    data: ItemCreate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Item:
    """Crea un item nuevo (del usuario logueado).

    - `data: ItemCreate`: FastAPI lee el JSON del body y lo valida contra el
      schema. Si algo no cuadra, responde 422 automáticamente.
    - `session = Depends(get_session)`: FastAPI nos inyecta una sesión de DB.
    - `status_code=201`: convención REST para "recurso creado".
    - `response_model=ItemRead`: la respuesta se filtra a esa forma.
    """
    # Convertimos el schema de entrada en un objeto de tabla `Item`.
    # `model_dump()` pasa los campos validados a un dict. El owner_id NO viene
    # del cliente (sería falsificable): sale del token ya verificado.
    item = Item(**data.model_dump(), owner_id=user.id)

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
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[Item]:
    """Devuelve los items DEL USUARIO, opcionalmente filtrados por tipo/estado.

    La consulta se construye por partes: partimos de "SELECT * FROM item WHERE
    owner_id = <yo>" y solo agregamos cada WHERE extra si el cliente mandó ese
    filtro. El filtro por dueño NO es opcional: va siempre.
    """
    query = select(Item).where(Item.owner_id == user.id)
    if kind is not None:
        query = query.where(Item.kind == kind)
    if item_status is not None:
        query = query.where(Item.status == item_status)

    items = session.exec(query).all()
    return list(items)


def _get_item_or_404(item_id: int, user: User, session: Session) -> Item:
    """Busca un item por id (del usuario dado) o lanza un error 404.

    Lo extraemos en una función porque ver, actualizar y borrar necesitan lo
    mismo: traer el item y, si no existe, responder "404 Not Found". Evita
    repetir el mismo bloque tres veces (principio DRY: Don't Repeat Yourself).

    Detalle de seguridad: si el item existe pero es de OTRO usuario, también
    respondemos 404 (no 403 "prohibido"). Un 403 confirmaría que ese id
    existe; el 404 no revela nada. Para el que pregunta, "no es tuyo" y
    "no existe" se ven idéntico.
    """
    item = session.get(Item, item_id)
    if item is None or item.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe un item con id {item_id}",
        )
    return item


@router.get("/{item_id}", response_model=ItemRead)
def get_item(
    item_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Item:
    """Devuelve un item puntual por su id (o 404 si no existe).

    `item_id` viene en la URL (p.ej. /items/3). FastAPI lo lee y lo convierte
    a int automáticamente; si no es un número, responde 422.
    """
    return _get_item_or_404(item_id, user, session)


@router.patch("/{item_id}", response_model=ItemRead)
def update_item(
    item_id: int,
    data: ItemUpdate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Item:
    """Actualiza parcialmente un item.

    Usamos PATCH (no PUT) porque es una edición PARCIAL: el cliente manda solo
    los campos que cambian. `exclude_unset=True` nos da únicamente esos campos.
    Esto es lo que usará el tablero al arrastrar una tarjeta de columna:
    un PATCH con solo {"status": "in_progress"}.
    """
    item = _get_item_or_404(item_id, user, session)

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
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> None:
    """Borra un item (o 404 si no existe).

    Responde 204 No Content: la convención REST para "borrado con éxito, no hay
    cuerpo que devolver". Por eso la función no retorna nada.
    """
    item = _get_item_or_404(item_id, user, session)
    session.delete(item)
    session.commit()
