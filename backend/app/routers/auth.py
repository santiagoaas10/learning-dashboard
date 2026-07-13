"""
Rutas de autenticación: registro, login y "¿quién soy?".

El flujo completo está explicado en app/security.py; aquí solo viven los
endpoints HTTP que lo exponen.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.models import User
from app.schemas import TokenResponse, UserCreate, UserRead
from app.security import create_access_token, get_current_user, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, session: Session = Depends(get_session)) -> TokenResponse:
    """Crea una cuenta nueva y devuelve el token directamente.

    Devolver el token aquí (en vez de solo "cuenta creada") ahorra un paso:
    el usuario queda logueado apenas se registra, sin tener que hacer login.
    """
    # ¿Ya existe una cuenta con este email? Normalizamos a minúsculas para que
    # "Santi@x.com" y "santi@x.com" cuenten como el mismo email.
    email = data.email.lower()
    existing = session.exec(select(User).where(User.email == email)).first()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,  # 409 = conflicto con el estado actual
            detail="Ya existe una cuenta con ese email.",
        )

    user = User(email=email, hashed_password=hash_password(data.password))
    session.add(user)
    session.commit()
    session.refresh(user)  # trae el id que asignó la base de datos

    return TokenResponse(access_token=create_access_token(user.id))


@router.post("/login", response_model=TokenResponse)
def login(data: UserCreate, session: Session = Depends(get_session)) -> TokenResponse:
    """Verifica credenciales y entrega el token de sesión."""
    user = session.exec(select(User).where(User.email == data.email.lower())).first()

    # Mismo error si el email no existe o si la contraseña no coincide: no
    # revelamos cuál de los dos falló (evita que alguien "sondee" qué emails
    # tienen cuenta, técnica llamada user enumeration).
    if user is None or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos.",
        )

    return TokenResponse(access_token=create_access_token(user.id))


@router.get("/me", response_model=UserRead)
def me(user: User = Depends(get_current_user)) -> User:
    """Devuelve la cuenta dueña del token.

    El frontend lo usa al abrir la página: si el token guardado sigue siendo
    válido responde 200 con el usuario; si venció responde 401 y se muestra
    la pantalla de login.
    """
    return user
