"""
Punto de entrada de la API.

Aquí se crea la instancia de FastAPI (el objeto `app`) que el servidor uvicorn
ejecuta. Este archivo "arma" la aplicación:
- crea las tablas de la base de datos al arrancar,
- habilita CORS para que el frontend de React pueda llamar a la API,
- enchufa los routers (las rutas agrupadas por recurso).
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import create_db_and_tables
from app.routers import items


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Código que corre al arrancar y al apagar la app.

    Todo lo que está ANTES del `yield` corre una vez al arrancar; lo de después
    correría al apagar. Aquí lo usamos para crear las tablas si no existen.
    Es el reemplazo moderno del antiguo `@app.on_event("startup")`.
    """
    create_db_and_tables()
    yield


app = FastAPI(
    title="Learning Dashboard API",
    version="0.1.0",
    description="API para trackear cursos y proyectos personales.",
    lifespan=lifespan,
)

# CORS = Cross-Origin Resource Sharing. El navegador bloquea por seguridad que
# una página (p.ej. React en http://localhost:5173) llame a una API en otro
# origen (http://127.0.0.1:8000) salvo que la API lo autorice explícitamente.
# Aquí autorizamos los orígenes locales de Vite durante el desarrollo.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_methods=["*"],   # permite GET, POST, PATCH, DELETE...
    allow_headers=["*"],
)

# Enchufamos las rutas de items. A partir de aquí existen /items, etc.
app.include_router(items.router)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Endpoint de salud: verifica de un vistazo que la API está viva."""
    return {"status": "ok"}
