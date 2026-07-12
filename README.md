# Learning Dashboard

Dashboard personal para trackear los cursos que quiero hacer (y, más adelante,
proyectos personales que quiero implementar).

Este es un proyecto de aprendizaje: el código está comentado a propósito para
que se entienda *por qué* se hace cada cosa, no solo *qué* hace.

## Stack

- **Backend:** [FastAPI](https://fastapi.tiangolo.com/) + [SQLModel](https://sqlmodel.tiangolo.com/) sobre SQLite.
- **Frontend:** React + Vite + TypeScript.
- **Base de datos:** SQLite (un solo archivo local, cero costo, cero setup de servidor).

## Estructura del proyecto

```
learning-dashboard/
├── backend/            # API en FastAPI
│   ├── app/            # código de la aplicación (modelos, rutas, db)
│   └── requirements.txt
└── frontend/           # interfaz en React + Vite + TypeScript
```

## Cómo correr el backend (v1)

```bash
cd backend
python -m venv .venv           # crea un entorno virtual aislado
source .venv/bin/activate      # actívalo (en macOS/Linux)
pip install -r requirements.txt
uvicorn app.main:app --reload  # levanta la API en http://127.0.0.1:8000
```

Con la API arriba, la documentación interactiva vive en:
http://127.0.0.1:8000/docs

## Alcance

- **v1 (actual):** CRUD de cursos + frontend mínimo para verlos y editarlos.
- **Siguiente:** proyectos personales, y a futuro agentes que trabajen sobre ellos.
