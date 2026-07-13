"""
Seguridad: hashing de contraseñas, tokens JWT y el "guardia" de las rutas.

Cómo funciona la sesión completa (el flujo que implementa este archivo):

1. REGISTRO: el usuario manda email + contraseña. Guardamos el email y el
   HASH de la contraseña (nunca la contraseña en sí).
2. LOGIN: comparamos el hash de lo que escribió contra el guardado. Si
   coincide, le damos un JWT: un "carnet" firmado por el servidor que dice
   "soy el usuario 5" y tiene fecha de vencimiento.
3. CADA REQUEST: el frontend manda ese carnet en el header
   `Authorization: Bearer <token>`. La dependencia `get_current_user`
   verifica la firma y nos entrega el usuario dueño del token.

El JWT va FIRMADO (no cifrado): cualquiera puede leer su contenido, pero
nadie puede modificarlo sin invalidar la firma, porque solo el servidor
conoce la SECRET_KEY. Por eso la clave jamás se commitea.
"""

import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session

from app.database import get_session
from app.models import User

# La clave con la que se firman los tokens. Viene de una variable de entorno;
# el valor por defecto es SOLO para desarrollo local. En producción se define
# una clave larga y aleatoria (p.ej. `openssl rand -hex 32`).
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-cambiar-en-produccion")
ALGORITHM = "HS256"  # algoritmo de firma estándar para JWT (HMAC + SHA-256)

# Cuánto dura la sesión. 7 días es cómodo para una app personal: no te pide
# login a cada rato, pero un token robado igual expira.
ACCESS_TOKEN_EXPIRE = timedelta(days=7)

# Esquema de seguridad: le dice a FastAPI que esperamos el header
# "Authorization: Bearer <token>". Además hace que /docs muestre el botón
# "Authorize" para probar endpoints protegidos pegando el token.
bearer_scheme = HTTPBearer()


# --- Contraseñas ---

def hash_password(plain: str) -> str:
    """Convierte la contraseña en un hash irreversible.

    bcrypt genera un "salt" (aleatorio) distinto por contraseña y lo incluye
    dentro del hash: dos usuarios con la misma contraseña tienen hashes
    diferentes, lo que frustra ataques con tablas precalculadas.
    """
    # bcrypt trabaja con bytes, no strings: encode() al entrar, decode() al salir.
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    """¿La contraseña escrita corresponde a este hash?"""
    return bcrypt.checkpw(plain.encode(), hashed.encode())


# --- Tokens JWT ---

def create_access_token(user_id: int) -> str:
    """Crea el token de sesión para un usuario.

    El "payload" lleva dos claims estándar:
    - sub (subject): a quién identifica el token. Va como string por convención.
    - exp (expiration): cuándo deja de valer. Las librerías lo verifican solas.
    """
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + ACCESS_TOKEN_EXPIRE,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    session: Session = Depends(get_session),
) -> User:
    """El "guardia" de las rutas protegidas.

    Cualquier endpoint que declare `user: User = Depends(get_current_user)`
    queda protegido: si el token falta, está vencido o es inválido, la request
    muere aquí con 401 y el endpoint ni se ejecuta.
    """
    # Un solo error genérico para todos los casos: no le damos pistas a un
    # atacante sobre QUÉ estuvo mal (¿token vencido? ¿usuario borrado?).
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Sesión inválida o vencida. Inicia sesión de nuevo.",
        headers={"WWW-Authenticate": "Bearer"},  # convención del estándar HTTP
    )

    try:
        # decode() verifica la firma Y la expiración en un solo paso.
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.InvalidTokenError:  # cubre firma inválida, token vencido, basura...
        raise unauthorized

    user = session.get(User, int(payload["sub"]))
    if user is None:  # el token era válido pero la cuenta ya no existe
        raise unauthorized

    return user
