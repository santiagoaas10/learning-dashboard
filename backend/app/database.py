"""
Configuración de la base de datos.

Aquí definimos tres cosas:
1. El "engine": el objeto que sabe cómo conectarse a la base de datos.
2. Una función para crear las tablas al arrancar.
3. Una "dependencia" de sesión que las rutas usarán para hablar con la DB.

La URL de conexión viene de la variable de entorno DATABASE_URL. Ese es el
patrón de "12-factor app": el MISMO código corre en cualquier ambiente y lo
único que cambia es la configuración:
- En desarrollo no defines nada y usas SQLite (un archivo local, cero costo).
- En producción defines DATABASE_URL apuntando a Postgres (Neon) y listo.
"""

import os
from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

# Si no hay variable de entorno, SQLite local: "sqlite:///<ruta-del-archivo>".
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///database.db")

# Los proveedores de Postgres suelen dar URLs "postgres://..." o
# "postgresql://...". SQLAlchemy necesita que especifiquemos el driver:
# "postgresql+psycopg://..." (psycopg es la librería que instalamos).
# Reescribimos el prefijo para aceptar cualquiera de las dos formas.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

_is_sqlite = DATABASE_URL.startswith("sqlite")

# El engine es el punto central de conexión. Se crea UNA sola vez y se reutiliza.
engine = create_engine(
    DATABASE_URL,
    # echo imprime en consola el SQL ejecutado. Útil para aprender en local;
    # en producción sería puro ruido en los logs, así que solo con SQLite.
    echo=_is_sqlite,
    # check_same_thread es una restricción exclusiva de SQLite (prohíbe usar
    # la conexión desde varios hilos). La desactivamos porque FastAPI atiende
    # requests en hilos distintos; es seguro con "una sesión por request".
    # Postgres no conoce ese parámetro, por eso el dict vacío en ese caso.
    connect_args={"check_same_thread": False} if _is_sqlite else {},
    # pool_pre_ping: antes de reusar una conexión del pool, verifica que siga
    # viva. Neon "duerme" las conexiones inactivas; sin esto, la primera
    # request tras un rato de silencio fallaría con una conexión muerta.
    pool_pre_ping=True,
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
