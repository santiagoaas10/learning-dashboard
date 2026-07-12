"""
Rutas del recurso "courses" (cursos).

Un `APIRouter` es como una mini-app: agrupa endpoints relacionados y luego se
"enchufa" a la app principal en main.py con `app.include_router(...)`. Así main
queda limpio y cada recurso vive en su propio archivo.

En este archivo, por ahora: crear un curso y listar todos.
"""

from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select

from app.database import get_session
from app.models import Course
from app.schemas import CourseCreate, CourseRead

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
