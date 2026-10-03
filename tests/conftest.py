"""Fixtures compartilhadas entre os testes."""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from taskflow.core.database import Base, get_db
from taskflow.main import app

TEST_EMAIL = "joao@exemplo.com"
TEST_PASSWORD = "senha-super-segura-123"


@pytest.fixture
def db() -> Generator[Session, None, None]:
    """Banco SQLite em memória, recriado para cada teste."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    session = session_factory()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db: Session) -> Generator[TestClient, None, None]:
    """TestClient do FastAPI com o banco de teste injetado."""

    def override_get_db() -> Generator[Session, None, None]:
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def registered_user(client: TestClient) -> dict[str, str]:
    """Cadastra um usuário e devolve email e senha."""
    response = client.post(
        "/auth/register",
        json={
            "email": TEST_EMAIL,
            "full_name": "João Victor",
            "password": TEST_PASSWORD,
        },
    )
    assert response.status_code == 201, response.text
    return {"email": TEST_EMAIL, "password": TEST_PASSWORD}


@pytest.fixture
def auth_headers(client: TestClient, registered_user: dict[str, str]) -> dict[str, str]:
    """Autentica o usuário de teste e devolve o header Authorization pronto."""
    response = client.post(
        "/auth/login",
        data={
            "username": registered_user["email"],
            "password": registered_user["password"],
        },
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}
