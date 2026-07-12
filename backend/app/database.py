"""
Configuración de la base de datos.

Aquí definimos tres cosas:
1. El "engine": el objeto que sabe cómo conectarse a la base de datos.
2. Una función para crear las tablas al arrancar.
3. Una "dependencia" de sesión que las rutas usarán para hablar con la DB.

Usamos SQLite, que guarda toda la base de datos en un solo archivo local
(`database.db`). Es perfecto para desarrollo: cero servidor, cero costo.
"""

from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

# URL de conexión. Para SQLite tiene la forma "sqlite:///<ruta-del-archivo>".
# El archivo se crea automáticamente la primera vez que se use.
DATABASE_URL = "sqlite:///database.db"

# El engine es el punto central de conexión. Se crea UNA sola vez y se reutiliza.
#
# connect_args={"check_same_thread": False}: por defecto SQLite prohíbe usar la
# misma conexión desde varios hilos. FastAPI puede atender requests en hilos
# distintos, así que desactivamos esa restricción. Es seguro con el patrón de
# "una sesión por request" que usamos abajo.
engine = create_engine(
    DATABASE_URL,
    echo=True,  # imprime en consola el SQL que se ejecuta (útil para aprender)
    connect_args={"check_same_thread": False},
)


def create_db_and_tables() -> None:
    """Crea las tablas en la base de datos.

    SQLModel.metadata conoce todos los modelos que heredan de SQLModel (con
    table=True). Esta función mira esos modelos y crea las tablas que falten.
    La llamaremos al arrancar la app.
    """
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Entrega una sesión de base de datos para una sola request.

    Una "sesión" es una conversación con la base de datos: dentro de ella se
    hacen consultas y cambios, y al final se confirman (commit) o se descartan.

    Esto es una "dependencia" de FastAPI: las rutas la piden con Depends() y
    FastAPI se encarga de crear la sesión antes de la request y cerrarla
    después (gracias al `with`, que garantiza el cierre incluso si hay error).
    """
    with Session(engine) as session:
        yield session
