"""
Rutas del recurso "courses" (cursos).

Un `APIRouter` es como una mini-app: agrupa endpoints relacionados y luego se
"enchufa" a la app principal en main.py con `app.include_router(...)`. Así main
queda limpio y cada recurso vive en su propio archivo.

En este archivo, por ahora: crear un curso y listar todos.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.models import Course, _now
from app.schemas import CourseCreate, CourseRead, CourseUpdate

# prefix="/courses": todas las rutas de aquí empiezan con /courses.
# tags=["courses"]: agrupa estos endpoints bajo un título en la doc /docs.
router = APIRouter(prefix="/courses", tags=["courses"])


@router.post("", response_model=CourseRead, status_code=status.HTTP_201_CREATED)
def create_course(
    data: CourseCreate,
    session: Session = Depends(get_session),
) -> Course:
    """Crea un curso nuevo.

    - `data: CourseCreate`: FastAPI lee el JSON del body y lo valida contra el
      schema. Si algo no cuadra, responde 422 automáticamente.
    - `session = Depends(get_session)`: FastAPI nos inyecta una sesión de DB.
    - `status_code=201`: convención REST para "recurso creado".
    - `response_model=CourseRead`: la respuesta se filtra a esa forma.
    """
    # Convertimos el schema de entrada en un objeto de tabla `Course`.
    # `model_dump()` pasa los campos validados a un dict; `Course(**dict)` crea la fila.
    course = Course(**data.model_dump())

    session.add(course)      # marca el objeto para insertarse
    session.commit()         # confirma: aquí se escribe de verdad en la DB
    session.refresh(course)  # recarga desde la DB para traer el id y las fechas
    return course


@router.get("", response_model=list[CourseRead])
def list_courses(
    session: Session = Depends(get_session),
) -> list[Course]:
    """Devuelve todos los cursos.

    `select(Course)` construye la consulta "SELECT * FROM course".
    `session.exec(...).all()` la ejecuta y devuelve la lista de resultados.
    """
    courses = session.exec(select(Course)).all()
    return list(courses)


def _get_course_or_404(course_id: int, session: Session) -> Course:
    """Busca un curso por id o lanza un error 404.

    Lo extraemos en una función porque ver, actualizar y borrar necesitan lo
    mismo: traer el curso y, si no existe, responder "404 Not Found". Evita
    repetir el mismo bloque tres veces (principio DRY: Don't Repeat Yourself).

    `session.get(Course, id)` es la forma directa de buscar por clave primaria.
    `HTTPException` hace que FastAPI corte y responda con ese código y mensaje.
    """
    course = session.get(Course, course_id)
    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe un curso con id {course_id}",
        )
    return course


@router.get("/{course_id}", response_model=CourseRead)
def get_course(
    course_id: int,
    session: Session = Depends(get_session),
) -> Course:
    """Devuelve un curso puntual por su id (o 404 si no existe).

    `course_id` viene en la URL (p.ej. /courses/3). FastAPI lo lee y lo convierte
    a int automáticamente; si no es un número, responde 422.
    """
    return _get_course_or_404(course_id, session)


@router.patch("/{course_id}", response_model=CourseRead)
def update_course(
    course_id: int,
    data: CourseUpdate,
    session: Session = Depends(get_session),
) -> Course:
    """Actualiza parcialmente un curso.

    Usamos PATCH (no PUT) porque es una edición PARCIAL: el cliente manda solo
    los campos que cambian. `exclude_unset=True` nos da únicamente esos campos.
    """
    course = _get_course_or_404(course_id, session)

    # Solo los campos que el cliente realmente envió.
    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(course, field, value)  # aplica cada cambio al objeto

    course.updated_at = _now()  # dejamos constancia de cuándo se editó

    session.add(course)
    session.commit()
    session.refresh(course)
    return course


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(
    course_id: int,
    session: Session = Depends(get_session),
) -> None:
    """Borra un curso (o 404 si no existe).

    Responde 204 No Content: la convención REST para "borrado con éxito, no hay
    cuerpo que devolver". Por eso la función no retorna nada.
    """
    course = _get_course_or_404(course_id, session)
    session.delete(course)
    session.commit()
