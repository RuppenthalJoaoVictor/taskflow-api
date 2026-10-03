# TaskFlow API

![CI](https://github.com/RuppenthalJoaoVictor/taskflow-api/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Code style](https://img.shields.io/badge/code%20style-Ruff-261230?style=for-the-badge)

API REST de gerenciamento de tarefas com **autenticação JWT**, **isolamento por
usuário**, **testes automatizados** e **CI/CD** — projeto de portfólio para
demonstrar boas práticas de desenvolvimento em Python.

> Status: 🚧 em desenvolvimento

## 📸 Documentação interativa

Ao rodar a aplicação localmente, a documentação fica disponível em
<http://localhost:8000/docs> (Swagger UI) e <http://localhost:8000/redoc>.

## 🎯 O problema que resolve

Organizar tarefas em planilhas e apps de bloco de notas é comum, mas esses
sistemas não estão acessíveis via API, não oferecem autenticação e são difíceis
de integrar com outros serviços. TaskFlow centraliza tarefas em uma API REST
simples, documentada e testada, pronta para ser consumida por um front-end ou
outro backend.

## ✨ Funcionalidades

- ✅ Cadastro de usuário com senha_hasheada em **bcrypt**
- ✅ Login com **JWT** e validação de token expirado/inválido
- ✅ CRUD completo de tarefas (`POST`, `GET`, `PATCH`, `DELETE`)
- ✅ **Isolamento de dados**: cada usuário só acessa as próprias tarefas
- ✅ Listagem paginada com filtro por status
- ✅ Marcação automática de `completed_at` ao concluir uma tarefa
- ✅ Documentação automática via OpenAPI/Swagger
- ✅ Validação de entrada com Pydantic v2
- ✅ Testes automatizados com cobertura
- ✅ CI com lint, type-check e testes em cada push

## 🛠️ Tecnologias

| Camada | Tecnologia |
| :--- | :--- |
| Linguagem | Python 3.11+ |
| Framework | FastAPI |
| Banco de dados | SQLite (dev) / SQLAlchemy 2.0 (ORM, troca fácil por PostgreSQL) |
| Autenticação | JWT (python-jose) + bcrypt (passlib) |
| Validação | Pydantic v2 + pydantic-settings |
| Testes | pytest + pytest-cov + httpx |
| Qualidade | Ruff (lint + format) + mypy (tipagem estrita) |
| CI | GitHub Actions |

## 🏗️ Estrutura do projeto

```text
taskflow-api/
├── src/
│   └── taskflow/
│       ├── api/
│       │   ├── deps.py            # dependências de auth e sessão
│       │   └── routes/
│       │       ├── auth.py         # register, login, me
│       │       └── tasks.py        # CRUD de tarefas
│       ├── core/
│       │   ├── config.py           # settings via env vars
│       │   ├── database.py        # engine, sessão, Base
│       │   └── security.py        # bcrypt + JWT
│       ├── models.py              # User e Task (SQLAlchemy ORM)
│       ├── schemas.py             # contratos de entrada/saída
│       └── main.py                # app FastAPI e middlewares
├── tests/
│   ├── conftest.py                # fixtures e banco em memória
│   ├── test_auth.py               # 10 testes de autenticação
│   └── test_tasks.py              # 13 testes de tarefas
├── .github/workflows/ci.yml       # lint + mypy + pytest
├── .env.example
└── pyproject.toml
```

## 🚀 Como executar

**Pré-requisitos:** Python 3.11 ou superior.

```bash
# 1. Clone e entre na pasta
git clone https://github.com/RuppenthalJoaoVictor/taskflow-api.git
cd taskflow-api

# 2. Crie o ambiente virtual
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Instale as dependências
pip install -e ".[dev]"

# 4. Configure as variáveis de ambiente
cp .env.example .env

# 5. Suba a aplicação
uvicorn taskflow.main:app --reload
```

Acesse <http://localhost:8000/docs> para testar os endpoints pela interface.

## 📡 Exemplos de uso

### Registrar e autenticar

```bash
# Registrar
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"voce@exemplo.com","full_name":"João Victor","password":"minha-senha-123"}'

# Login (retorna o token)
curl -X POST http://localhost:8000/auth/login \
  -d "username=voce@exemplo.com&password=minha-senha-123"
```

### Criar e listar tarefas

```bash
TOKEN="seu-token-aqui"

# Criar
curl -X POST http://localhost:8000/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Estudar Python","description":"Revisar async/await"}'

# Listar concluídas
curl "http://localhost:8000/tasks?completed=false" \
  -H "Authorization: Bearer $TOKEN"

# Concluir
curl -X PATCH http://localhost:8000/tasks/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"completed":true}'
```

## 🧪 Testes e qualidade

```bash
pytest                    # roda a suíte com relatório de cobertura
pytest --cov-report=html  # gera relatório HTML em htmlcov/
ruff check .              # lint
ruff format --check .     # verifica formatação
mypy src                  # verificação de tipos
```

## 🧠 Decisões de projeto

- **SQLAlchemy 2.0 com padrão `Mapped`/`mapped_column`** em vez de `declarative_base`
  clássico: mais tipado e idiomático na versão atual.
- **Repository pattern simplificado** — a lógica de acesso fica em
  `api/routes/`, isolada de forma que possa ser movida para um `repositories/`
  sem alterar as rotas.
- **`404` em vez de `403` para recursos de outro usuário**, evitando vazar a
  existência de dados que não pertencem a quem requisita.
- **Configuração por `pydantic-settings`** para que nenhuma credencial fique
  hardcoded — trocável por variável de ambiente em produção.
- **Testes com SQLite em memória e `StaticPool`**, que é a forma mais rápida de
  testar SQLAlchemy sem subir um banco real.

## 📄 Licença

Distribuído sob a licença MIT. Veja o arquivo [LICENSE](LICENSE).

## 👤 Autor

**João Victor Amaral Ruppenthal** — [@RuppenthalJoaoVictor](https://github.com/RuppenthalJoaoVictor)

Este projeto existe como demonstração pública de estudos em Python e boas práticas
de API. Contribuições são bem-vindas!