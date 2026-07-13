"""
Punto de entrada del backend en Vercel.

En Vercel no hay un servidor uvicorn corriendo 24/7: cada archivo dentro de
`api/` se convierte en una "serverless function" que despierta cuando llega
una request. Este archivo expone nuestra app de FastAPI como esa function.

El vercel.json de la raíz redirige todo `/api/*` hacia aquí. Como FastAPI
tiene sus rutas SIN el prefijo (/auth/login, /items...), este wrapper le
quita el "/api" inicial al path antes de entregarle la request: el navegador
pide /api/auth/login y FastAPI ve /auth/login. Así el mismo backend corre
igual en local (uvicorn) y en Vercel, sin duplicar rutas.
"""

import sys
from pathlib import Path

# El código del backend vive en backend/, no junto a este archivo. Agregamos
# esa carpeta a la lista de lugares donde Python busca imports (sys.path)
# para que "from app.main import ..." funcione también aquí.
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.main import app as fastapi_app  # noqa: E402  (import tras tocar sys.path)


async def app(scope, receive, send):
    """Envoltura ASGI mínima que quita el prefijo /api del path.

    ASGI es el "enchufe" estándar entre servidores y apps Python (FastAPI lo
    habla nativamente). `scope` describe la request (método, path, headers...);
    aquí solo retocamos el path y delegamos todo lo demás a FastAPI.
    """
    if scope["type"] == "http" and scope.get("path", "").startswith("/api"):
        scope = dict(scope)  # copiamos: no se debe mutar el scope original
        scope["path"] = scope["path"][len("/api") :] or "/"
        # raw_path es la versión en bytes del path; algunas piezas la usan.
        raw_path = scope.get("raw_path")
        if raw_path:
            scope["raw_path"] = raw_path[len(b"/api") :] or b"/"

    await fastapi_app(scope, receive, send)
