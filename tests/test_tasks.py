"""Testes do CRUD de tarefas e do isolamento entre usuários."""

from fastapi.testclient import TestClient


def _criar_tarefa(client: TestClient, headers: dict[str, str], titulo: str) -> dict:
    """Atalho para criar uma tarefa e devolver o corpo da resposta."""
    response = client.post("/tasks", headers=headers, json={"title": titulo})
    assert response.status_code == 201, response.text
    return response.json()


def test_criar_tarefa(client: TestClient, auth_headers: dict[str, str]) -> None:
    """Uma tarefa criada deve voltar com id, completed=False e sem completed_at."""
    task = _criar_tarefa(client, auth_headers, "Estudar FastAPI")

    assert task["title"] == "Estudar FastAPI"
    assert task["completed"] is False
    assert task["completed_at"] is None
    assert isinstance(task["id"], int)


def test_criar_tarefa_com_descricao(client: TestClient, auth_headers: dict[str, str]) -> None:
    """A descrição é opcional, mas deve ser salva quando enviada."""
    task = _criar_tarefa(client, auth_headers, "Escrever testes")
    assert task["description"] is None

    response = client.post(
        "/tasks",
        headers=auth_headers,
        json={"title": "Refatorar", "description": "Extrair função duplicada"},
    )
    assert response.json()["description"] == "Extrair função duplicada"


def test_criar_tarefa_com_titulo_vazio(client: TestClient, auth_headers: dict[str, str]) -> None:
    """Títulos que só têm espaços devem ser rejeitados com 422."""
    response = client.post("/tasks", headers=auth_headers, json={"title": "    "})
    assert response.status_code == 422


def test_criar_tarefa_exige_autenticacao(client: TestClient) -> None:
    """Não deve ser possível criar tarefas sem token."""
    assert client.post("/tasks", json={"title": "Sem token"}).status_code == 401


def test_listar_tarefas(client: TestClient, auth_headers: dict[str, str]) -> None:
    """A listagem deve retornar as tarefas do usuário com total correto."""
    _criar_tarefa(client, auth_headers, "Tarefa A")
    _criar_tarefa(client, auth_headers, "Tarefa B")

    response = client.get("/tasks", headers=auth_headers)
    assert response.status_code == 200

    body = response.json()
    assert body["total"] == 2
    assert body["skip"] == 0
    assert len(body["items"]) == 2


def test_listar_tarefas_paginacao(client: TestClient, auth_headers: dict[str, str]) -> None:
    """skip e limit devem controlar a quantidade devolvida."""
    for i in range(5):
        _criar_tarefa(client, auth_headers, f"Tarefa {i}")

    response = client.get("/tasks", headers=auth_headers, params={"skip": 1, "limit": 2})
    body = response.json()

    assert body["total"] == 5
    assert len(body["items"]) == 2


def test_listar_tarefas_filtro_por_status(client: TestClient, auth_headers: dict[str, str]) -> None:
    """O filtro completed deve separar concluídas de pendentes."""
    _criar_tarefa(client, auth_headers, "Pendente")
    _criar_tarefa(client, auth_headers, "Concluida")

    client.patch("/tasks/2", headers=auth_headers, json={"completed": True})

    pendentes = client.get("/tasks", headers=auth_headers, params={"completed": False}).json()
    concluidas = client.get("/tasks", headers=auth_headers, params={"completed": True}).json()

    assert pendentes["total"] == 1
    assert concluidas["total"] == 1
    assert concluidas["items"][0]["title"] == "Concluida"


def test_atualizar_tarefa_marca_conclusao_e_timestamp(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    """Concluir uma tarefa deve preencher completed_at."""
    task = _criar_tarefa(client, auth_headers, "Revisar PR")

    response = client.patch(f"/tasks/{task['id']}", headers=auth_headers, json={"completed": True})
    assert response.status_code == 200

    body = response.json()
    assert body["completed"] is True
    assert body["completed_at"] is not None


def test_reabrir_tarefa_limpa_timestamp(client: TestClient, auth_headers: dict[str, str]) -> None:
    """Reabrir uma tarefa deve limpar o completed_at."""
    task = _criar_tarefa(client, auth_headers, "Reabrir")
    client.patch(f"/tasks/{task['id']}", headers=auth_headers, json={"completed": True})

    response = client.patch(f"/tasks/{task['id']}", headers=auth_headers, json={"completed": False})
    assert response.json()["completed"] is False
    assert response.json()["completed_at"] is None


def test_atualizar_tarefa_parcialmente(client: TestClient, auth_headers: dict[str, str]) -> None:
    """Um PATCH deve alterar apenas os campos enviados."""
    task = _criar_tarefa(client, auth_headers, "Título original")

    response = client.patch(f"/tasks/{task['id']}", headers=auth_headers, json={"title": "Novo"})
    assert response.status_code == 200
    assert response.json()["title"] == "Novo"


def test_obter_tarefa_inexistente(client: TestClient, auth_headers: dict[str, str]) -> None:
    """Consultar um id inexistente deve retornar 404."""
    assert client.get("/tasks/9999", headers=auth_headers).status_code == 404


def test_deletar_tarefa(client: TestClient, auth_headers: dict[str, str]) -> None:
    """Após o DELETE, a tarefa não deve mais ser encontrada."""
    task = _criar_tarefa(client, auth_headers, "Temporária")

    assert client.delete(f"/tasks/{task['id']}", headers=auth_headers).status_code == 204
    assert client.get(f"/tasks/{task['id']}", headers=auth_headers).status_code == 404


def test_usuario_nao_acessa_tarefa_de_outro(client: TestClient) -> None:
    """Cada usuário deve ver apenas as próprias tarefas (isolamento por owner_id)."""
    user_a = client.post(
        "/auth/register",
        json={"email": "a@exemplo.com", "full_name": "Usuário A", "password": "senha-a-12345"},
    )
    assert user_a.status_code == 201
    token_a = client.post(
        "/auth/login", data={"username": "a@exemplo.com", "password": "senha-a-12345"}
    ).json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    task = _criar_tarefa(client, headers_a, "Tarefa privada do A")

    client.post(
        "/auth/register",
        json={"email": "b@exemplo.com", "full_name": "Usuário B", "password": "senha-b-12345"},
    )
    token_b = client.post(
        "/auth/login", data={"username": "b@exemplo.com", "password": "senha-b-12345"}
    ).json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # B não deve enxergar a task do A em nenhuma operação.
    assert client.get("/tasks", headers=headers_b).json()["total"] == 0
    assert client.get(f"/tasks/{task['id']}", headers=headers_b).status_code == 404

    patch = client.patch(f"/tasks/{task['id']}", headers=headers_b, json={"title": "hack"})
    assert patch.status_code == 404

    assert client.delete(f"/tasks/{task['id']}", headers=headers_b).status_code == 404
