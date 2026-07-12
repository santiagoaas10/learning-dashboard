"""
Punto de entrada de la API.

Aquí se crea la instancia de FastAPI (el objeto `app`) que el servidor uvicorn
ejecuta. Por ahora solo tiene un endpoint de "salud" para comprobar que todo
levanta bien; en los siguientes commits le iremos colgando el CRUD de cursos.
"""

from fastapi import FastAPI

# `app` es la aplicación. `title` y `version` aparecen en la documentación
# automática que FastAPI genera en /docs (una de sus mejores features).
app = FastAPI(
    title="Learning Dashboard API",
    version="0.1.0",
    description="API para trackear cursos y proyectos personales.",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Endpoint de salud.

    Sirve para verificar de un vistazo que la API está viva. Los sistemas de
    monitoreo y despliegue suelen llamar a un endpoint así para saber si el
    servicio responde. Devolver un dict hace que FastAPI responda un JSON.
    """
    return {"status": "ok"}
