"""Testes das rotas de autenticação."""

from conftest import TEST_EMAIL, TEST_PASSWORD
from fastapi.testclient import TestClient


def test_health_check(client: TestClient) -> None:
    """O health check deve responder ok sem exigir autenticação."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_registrar_usuario(client: TestClient) -> None:
    """Um novo usuário deve ser criado e nunca expor o hash da senha."""
    response = client.post(
        "/auth/register",
        json={"email": TEST_EMAIL, "full_name": "João Victor", "password": TEST_PASSWORD},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == TEST_EMAIL
    assert body["full_name"] == "João Victor"
    assert "password" not in body
    assert "hashed_password" not in body


def test_registrar_email_duplicado(client: TestClient) -> None:
    """Cadastrar o mesmo e-mail duas vezes deve retornar 409."""
    payload = {"email": TEST_EMAIL, "full_name": "João", "password": TEST_PASSWORD}
    assert client.post("/auth/register", json=payload).status_code == 201

    response = client.post("/auth/register", json=payload)
    assert response.status_code == 409


def test_registrar_senha_curta(client: TestClient) -> None:
    """Senhas abaixo de 8 caracteres devem ser rejeitadas pelo schema."""
    response = client.post(
        "/auth/register",
        json={"email": TEST_EMAIL, "full_name": "João", "password": "curta"},
    )
    assert response.status_code == 422


def test_registrar_email_invalido(client: TestClient) -> None:
    """E-mails malformados devem ser rejeitados pela validação do Pydantic."""
    response = client.post(
        "/auth/register",
        json={"email": "nao-e-um-email", "full_name": "João", "password": TEST_PASSWORD},
    )
    assert response.status_code == 422


def test_nome_com_espacos_excessivos_e_sanado(client: TestClient) -> None:
    """O validator deve remover espaços nas pontas do nome."""
    response = client.post(
        "/auth/register",
        json={"email": TEST_EMAIL, "full_name": "   João Victor   ", "password": TEST_PASSWORD},
    )
    assert response.status_code == 201
    assert response.json()["full_name"] == "João Victor"


def test_login_valido(client: TestClient, registered_user: dict[str, str]) -> None:
    """Credenciais corretas devem retornar um token JWT."""
    response = client.post(
        "/auth/login",
        data={"username": registered_user["email"], "password": registered_user["password"]},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert len(body["access_token"]) > 20


def test_login_com_senha_errada(client: TestClient, registered_user: dict[str, str]) -> None:
    """Senha incorreta deve retornar 401."""
    response = client.post(
        "/auth/login",
        data={"username": registered_user["email"], "password": "senha-errada-999"},
    )
    assert response.status_code == 401


def test_login_usuario_inexistente(client: TestClient) -> None:
    """E-mail não cadastrado deve retornar 401, sem revelar se existe."""
    response = client.post(
        "/auth/login",
        data={"username": "ninguem@exemplo.com", "password": TEST_PASSWORD},
    )
    assert response.status_code == 401


def test_me_com_token_valido(
    client: TestClient, registered_user: dict[str, str], auth_headers: dict[str, str]
) -> None:
    """Com token válido, /auth/me deve devolver os dados do usuário."""
    response = client.get("/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == registered_user["email"]


def test_me_sem_token(client: TestClient) -> None:
    """Rotas protegidas devem retornar 401 quando o header Authorization falta."""
    assert client.get("/auth/me").status_code == 401


def test_me_com_token_invalido(client: TestClient) -> None:
    """Um token adulterado deve ser rejeitado."""
    response = client.get("/auth/me", headers={"Authorization": "Bearer token.invalido.aqui"})
    assert response.status_code == 401
