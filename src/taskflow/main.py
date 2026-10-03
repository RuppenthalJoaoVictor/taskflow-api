"""Ponto de entrada da aplicação."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from taskflow.api.routes import auth, tasks
from taskflow.core.config import get_settings
from taskflow.core.database import Base, engine

settings = get_settings()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "API REST para gerenciamento de tarefas com autenticação JWT. "
        "Feita como projeto de portfólio para demonstração de boas práticas em Python."
    ),
    license_info={"name": "MIT"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(tasks.router)


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    """Endpoint de health check, útil para deploy e monitoramento."""
    return {"status": "ok", "version": settings.app_version}


@app.get("/", tags=["system"])
def root() -> dict[str, str]:
    """Endpoint raiz com um link para a documentação."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
    }
